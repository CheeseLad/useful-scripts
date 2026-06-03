#!/usr/bin/env python3

"""
Minecraft Latest Backup Copier

Finds the most recent backup ZIP inside each world folder
and copies it to a destination folder.

Features:
- Ignores world name in ZIP filename
- Copies ONLY the newest backup per world
- Dry run mode
- Skip specific folders
- Preserves original ZIP files
- Optional overwrite protection

Example filenames:
    2020-12-28_00-19-11_Skyblock 4.zip
    2020-12-28_00-40-48_Anything.zip
"""

from pathlib import Path
from datetime import datetime
import re
import argparse
import shutil

# ==========================================
# IGNORE THESE WORLD FOLDERS
# ==========================================
IGNORED_FOLDERS = {
    "+ Folders",
    "+ Single Backups",
}

# ==========================================
# LOG FILE
# ==========================================
LOG_FILE = f"./logs/copy_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Match timestamp at beginning only
TIMESTAMP_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})"
)


def log(message):
    """
    Print to console and append to log file.
    """

    print(message)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def extract_timestamp(filename):
    match = TIMESTAMP_PATTERN.match(filename)

    if not match:
        return None

    timestamp_str = f"{match.group(1)}_{match.group(2)}"

    try:
        return datetime.strptime(
            timestamp_str,
            "%Y-%m-%d_%H-%M-%S"
        )
    except ValueError:
        return None


def format_gb(num_bytes):
    return f"{num_bytes / (1024 ** 3):.2f} GB"


def find_latest_backup(world_folder):
    """
    Return the newest ZIP backup in a world folder.
    """

    newest_backup = None
    newest_timestamp = None

    for zip_file in world_folder.glob("*.zip"):

        timestamp = extract_timestamp(zip_file.name)

        if not timestamp:
            log(f"[SKIP] Invalid filename: {zip_file.name}")
            continue

        if (
            newest_timestamp is None
            or timestamp > newest_timestamp
        ):
            newest_timestamp = timestamp
            newest_backup = zip_file

    return newest_backup, newest_timestamp


def process_world_folder(
    world_folder,
    destination_folder,
    dry_run=False,
    overwrite=False
):
    latest_backup, timestamp = find_latest_backup(world_folder)

    if not latest_backup:
        log(f"[NO BACKUPS] {world_folder.name}")
        return 0

    destination_file = destination_folder / latest_backup.name

    if destination_file.exists() and not overwrite:
        log(
            f"[EXISTS] {destination_file.name} "
            f"(use --overwrite to replace)"
        )
        return 0

    size_bytes = latest_backup.stat().st_size

    log(f"\n[{world_folder.name}]")
    log(f"LATEST : {latest_backup.name}")
    log(f"SIZE   : {format_gb(size_bytes)}")
    log(f"COPY TO: {destination_file}")

    if not dry_run:
        shutil.copy2(latest_backup, destination_file)

    return size_bytes


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "root_folder",
        help="Folder containing Minecraft world folders"
    )

    parser.add_argument(
        "destination_folder",
        help="Folder to copy newest backups into"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview copy operations only"
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite files in destination"
    )

    args = parser.parse_args()

    root = Path(args.root_folder)
    destination = Path(args.destination_folder)

    if not root.exists():
        log(f"Root folder not found: {root}")
        return

    destination.mkdir(parents=True, exist_ok=True)

    total_copied = 0
    total_bytes = 0

    for subfolder in root.iterdir():

        if not subfolder.is_dir():
            continue

        # Ignore configured folders
        if subfolder.name in IGNORED_FOLDERS:
            log(f"[IGNORED] {subfolder.name}")
            continue

        copied_bytes = process_world_folder(
            subfolder,
            destination,
            dry_run=args.dry_run,
            overwrite=args.overwrite
        )

        if copied_bytes > 0:
            total_copied += 1
            total_bytes += copied_bytes

    log("\nFinished.")

    if args.dry_run:
        log("\n=== DRY RUN SUMMARY ===")
        log(f"Files that would be copied : {total_copied}")
        log(f"Total size                 : {format_gb(total_bytes)}")
    else:
        log("\n=== FINAL SUMMARY ===")
        log(f"Files copied : {total_copied}")
        log(f"Total size   : {format_gb(total_bytes)}")


if __name__ == "__main__":
    main()