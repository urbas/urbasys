#!/usr/bin/env python

import click
import logging
from datetime import datetime
from shutil import rmtree
from pathlib import Path
from typing import Dict, Iterable, List, Set

from dateutil.parser import isoparse

from urbasys.log_utils import setup_logging


BACKUP_ROOT_DIR = "/urbackup/mirror"


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet", count=True)
def main(verbose, quiet):
    setup_logging(verbose, quiet)


@main.command(name="retain-monthlies", help="Keeps one backup snapshot per month.")
@click.argument(
    "backups-root-dirs",
    nargs=-1,
    type=click.Path(path_type=Path, dir_okay=True, exists=True),
)
@click.option("-n", "--dry-run", is_flag=True)
@click.option(
    "--keep-latest",
    default=30,
    type=int,
    help="The number of latest snapshots to keep. "
    "After that only the oldest snapshot of the month will be kept.",
)
def retain_monthlies(
    backups_root_dirs: Iterable[Path], dry_run: bool, keep_latest: int
) -> None:
    for backup_root_dir in backups_root_dirs:
        snapshot_dirs = [
            snapshot_dir
            for snapshot_dir in backup_root_dir.glob("daily-*Z")
            if snapshot_dir.is_dir()
        ]
        dates_2_snapshot_dirs = {
            folder_to_datetime(snapshot_dir): snapshot_dir
            for snapshot_dir in snapshot_dirs
        }
        all_dates = dates_2_snapshot_dirs.keys()
        dates_to_retain = backups_to_keep(all_dates, keep_latest)
        for date_to_remove in sorted(set(all_dates) - dates_to_retain):
            if dry_run:
                logging.info("Would remove %s", dates_2_snapshot_dirs[date_to_remove])
                continue
            logging.info("Removing %s...", dates_2_snapshot_dirs[date_to_remove])
            rmtree(dates_2_snapshot_dirs[date_to_remove])


def folder_to_datetime(path: Path) -> datetime:
    return isoparse(path.name[6:])


def keep_last(backup_dates: Iterable[datetime], number_to_keep: int) -> List[datetime]:
    return sorted(backup_dates, reverse=True)[:number_to_keep]


def monthlies_to_keep(backup_dates: Iterable[datetime]) -> Set[datetime]:
    month_buckets: Dict[int, datetime] = {}
    for cur_backup_date in backup_dates:
        current_month = cur_backup_date.month
        existing_backup_date = month_buckets.get(current_month)
        if existing_backup_date is None or cur_backup_date < existing_backup_date:
            month_buckets[current_month] = cur_backup_date
    return set(month_buckets.values())


def backups_to_keep(
    snapshot_dates: Iterable[datetime], keep_latest: int
) -> Set[datetime]:
    last_dates = set(keep_last(snapshot_dates, keep_latest))
    monthlies = monthlies_to_keep(snapshot_dates)
    return last_dates.union(monthlies)
