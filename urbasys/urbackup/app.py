import click
from datetime import timedelta
from pathlib import Path
from typing import Iterable

# this library does not come with type stubs, so we tell mypy to ignore it
import pytimeparse  # type: ignore

from urbasys import log_utils
from urbasys.urbackup import retention


BACKUP_ROOT_DIR = "/urbackup/mirror"


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet", count=True)
def main(verbose, quiet):
    log_utils.setup_logging(verbose, quiet)


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
        retention.retain_monthlies(backup_root_dir, dry_run, keep_latest)


@main.command(
    name="delete-old",
    help="Deletes backup folders older than a certain amount of time.",
)
@click.argument(
    "backups-root-dirs",
    nargs=-1,
    type=click.Path(path_type=Path, dir_okay=True, exists=True),
)
@click.option("-n", "--dry-run", is_flag=True)
@click.option(
    "--max-age",
    required=True,
    type=lambda arg: timedelta(seconds=pytimeparse.parse(arg)),
    help="Snapshots older than this will be deleted.",
)
@click.option(
    "--min-keep",
    default=5,
    type=int,
    help="The minimum number of snapshots to keep (even if they are older than `--max-age`).",
)
def delete_old(
    backups_root_dirs: Iterable[Path], dry_run: bool, max_age: timedelta, min_keep: int
) -> None:
    for backup_root_dir in backups_root_dirs:
        retention.delete_old(backup_root_dir, dry_run, max_age, min_keep)
