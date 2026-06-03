#!/usr/bin/env python3

"""
Minecraft Backup Cleanup Script

Keeps only the newest backup per day inside each world folder.

Features:
- Ignores world name in ZIP filename
- Dry run mode
- Reports reclaimed GB
- Ignore specific subfolders

Example filenames:
    2020-12-28_00-19-11_Skyblock 4.zip
    2020-12-28_00-40-48_Anything.zip
"""

from pathlib import Path
from datetime import datetime
import re
import argparse

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
LOG_FILE = f"./logs/cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

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


def process_world_folder(world_folder, dry_run=False):
    backups_by_day = {}

    for zip_file in world_folder.glob("*.zip"):

        timestamp = extract_timestamp(zip_file.name)

        if not timestamp:
            log(f"[SKIP] Invalid filename: {zip_file.name}")
            continue

        day = timestamp.date()

        backups_by_day.setdefault(day, []).append(
            (timestamp, zip_file)
        )

    deleted_count = 0
    deleted_bytes = 0

    for day, backups in backups_by_day.items():

        # newest first
        backups.sort(key=lambda x: x[0], reverse=True)

        keep = backups[0][1]

        log(f"\n[{world_folder.name}] {day}")
        log(f"KEEP   : {keep.name}")

        for _, old_backup in backups[1:]:

            size_bytes = old_backup.stat().st_size
            deleted_bytes += size_bytes

            log(
                f"DELETE : {old_backup.name} "
                f"({format_gb(size_bytes)})"
            )

            if not dry_run:
                old_backup.unlink()

            deleted_count += 1

    return deleted_count, deleted_bytes


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "root_folder",
        help="Folder containing Minecraft world folders"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview deletions only"
    )

    args = parser.parse_args()

    root = Path(args.root_folder)

    if not root.exists():
        log(f"Folder not found: {root}")
        return

    total_deleted = 0
    total_bytes = 0

    for subfolder in root.iterdir():

        if not subfolder.is_dir():
            continue

        # Ignore configured folders
        if subfolder.name in IGNORED_FOLDERS:
            log(f"[IGNORED] {subfolder.name}")
            continue

        deleted_count, deleted_bytes = process_world_folder(
            subfolder,
            dry_run=args.dry_run
        )

        total_deleted += deleted_count
        total_bytes += deleted_bytes

    log("\nFinished.")

    if args.dry_run:
        log("\n=== DRY RUN SUMMARY ===")
        log(f"Files that would be deleted : {total_deleted}")
        log(f"Space that would be freed   : {format_gb(total_bytes)}")
    else:
        log("\n=== FINAL SUMMARY ===")
        log(f"Files deleted : {total_deleted}")
        log(f"Space freed   : {format_gb(total_bytes)}")


if __name__ == "__main__":
    main()