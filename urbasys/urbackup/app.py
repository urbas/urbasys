#!/usr/bin/env python

import click
import logging
from datetime import datetime, timedelta
from glob import glob
from os.path import join, basename
from shutil import rmtree
from socket import getfqdn
from subprocess import check_call

from urbasys.log_utils import setup_logging


BACKUP_ROOT_DIR = "/urbackup/mirror"


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet", count=True)
def main(verbose, quiet):
    setup_logging(verbose, quiet)


@main.command(name="create-daily-backup")
@click.argument("remote_host")
def create_daily_backup(remote_host):
    fqdn = getfqdn()
    timestamp = datetime.utcnow().isoformat()[:-3]
    todays_backup_dir = "daily-{}Z".format(timestamp)
    backup_root_dir = join(BACKUP_ROOT_DIR, fqdn)
    dest_dir = join(backup_root_dir, todays_backup_dir)
    remote_user = "pi"
    connection_string = "{}@{}".format(remote_user, remote_host)
    rsync_target = "{}:{}".format(connection_string, dest_dir)
    source_dir = "/urbackup/local"

    logging.info("Backing up '%s' to '%s'", source_dir, rsync_target)

    ssh_conf = [
        "ssh",
        "-i",
        "/home/pi/.ssh/pi_to_pi_id_rsa",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "LogLevel=ERROR",
    ]
    ssh_cmd = ssh_conf + [connection_string]

    create_backup_root_dir(ssh_cmd, remote_user, backup_root_dir)
    incremental_rsync(ssh_conf, backup_root_dir, source_dir, rsync_target)
    complete_dir(ssh_cmd, dest_dir)
    create_latest_link(ssh_cmd, backup_root_dir, dest_dir)

    logging.info("Backup of '%s' to '%s' finished.", source_dir, rsync_target)


@main.command(name="remove-old-backups")
@click.option("-n", "--dry-run", is_flag=True)
@click.option("--backups-root-dir", default=BACKUP_ROOT_DIR)
def remove_old_backups(dry_run, backups_root_dir):
    for backup_dir in glob("{}/*/".format(backups_root_dir)):
        daily_backups = glob("{}/daily-*Z".format(backup_dir))
        all_dates = [
            folder_to_datetime(basename(daily_backup)) for daily_backup in daily_backups
        ]
        dates_2_folders = dict(zip(all_dates, daily_backups))
        dates_to_retain = backups_to_keep(
            all_dates,
            days_to_keep_dailies=30,
            current_date=datetime.now(),
            minimum_backups=30,
        )
        for date_to_remove in sorted(set(all_dates) - dates_to_retain):
            if dry_run:
                logging.info("Would remove {}".format(dates_2_folders[date_to_remove]))
                continue
            logging.info("Removing {}...".format(dates_2_folders[date_to_remove]))
            rmtree(dates_2_folders[date_to_remove])


def create_latest_link(ssh_cmd, backup_root_dir, dest_dir):
    check_call(
        ssh_cmd
        + [
            "ln -snf '{dest_dir}' '{backup_root_dir}/.latest'".format(
                dest_dir=dest_dir, backup_root_dir=backup_root_dir
            )
        ]
    )


def incremental_rsync(ssh_conf, backup_root_dir, source_dir, rsync_target):
    check_call(
        [
            "rsync",
            "-e",
            " ".join(ssh_conf),
            "--link-dest",
            "{}/.latest".format(backup_root_dir),
            "-Pav",
            source_dir + "/",
            rsync_target + ".incomplete/",
        ]
    )


def complete_dir(ssh_cmd, dest_dir):
    check_call(
        ssh_cmd + ["mv {dest_dir}.incomplete {dest_dir}".format(dest_dir=dest_dir)]
    )


def create_backup_root_dir(ssh_cmd, dir_owner, backup_root_dir):
    check_call(
        ssh_cmd
        + [
            "sudo mkdir -p {backup_root_dir}/; sudo chown {remote_user} {backup_root_dir}".format(
                backup_root_dir=backup_root_dir, remote_user=dir_owner
            )
        ]
    )


def folder_to_datetime(folder_name):
    return datetime.strptime(folder_name[6:], "%Y-%m-%dT%H:%M:%S.%fZ")


def dailies_to_keep(backup_dates, days_to_keep, current_date, minimum_backups=None):
    all_dates = sorted(backup_dates, reverse=True)
    automatically_kept = [] if minimum_backups is None else all_dates[:minimum_backups]
    to_be_filtered = (
        all_dates if minimum_backups is None else all_dates[minimum_backups:]
    )
    max_age = timedelta(days=days_to_keep)
    return automatically_kept + [
        backup_date
        for backup_date in to_be_filtered
        if current_date - backup_date <= max_age
    ]


def monthlies_to_keep(backup_dates):
    month_buckets = {}
    for cur_backup_date in backup_dates:
        current_month = cur_backup_date.month
        existing_backup_date = month_buckets.get(current_month)
        if existing_backup_date is None or cur_backup_date < existing_backup_date:
            month_buckets[current_month] = cur_backup_date
    return set(month_buckets.values())


def backups_to_keep(
    all_backup_dates, days_to_keep_dailies, current_date, minimum_backups=None
):
    dailies = set(
        dailies_to_keep(
            all_backup_dates, days_to_keep_dailies, current_date, minimum_backups
        )
    )
    monthlies = monthlies_to_keep(all_backup_dates)
    return dailies.union(monthlies)


if __name__ == "__main__":
    main()
