#!/usr/bin/env python3
"""
Log Archiving Script

Archives log files older than 14 days when total log size exceeds 1GB.
Designed to run on session startup/shutdown or as a scheduled task.

Usage:
    python helpers/archive_logs.py                  # Run with defaults
    python helpers/archive_logs.py --check          # Check status only, no archiving
    python helpers/archive_logs.py --force          # Archive regardless of size threshold
    python helpers/archive_logs.py --days 7         # Custom age threshold
    python helpers/archive_logs.py --size 500       # Custom size threshold in MB

Log files detected:
    - claudeLog.md
    - slack_listener.log
    - Any *.log files in project root or stock_analysis/
"""

import argparse
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
ARCHIVE_DIR = PROJECT_ROOT / "archives" / "logs"
DEFAULT_AGE_DAYS = 14
DEFAULT_SIZE_MB = 1024  # 1GB

# Log file patterns to check
LOG_PATTERNS = [
    ("claudeLog.md", PROJECT_ROOT),
    ("claudeLog_*.md", PROJECT_ROOT),
    ("slack_listener.log", PROJECT_ROOT / "stock_analysis"),
    ("*.log", PROJECT_ROOT),
    ("*.log", PROJECT_ROOT / "stock_analysis"),
]


def get_log_files() -> list[Path]:
    """Find all log files in the project."""
    log_files = []
    seen = set()

    for pattern, directory in LOG_PATTERNS:
        if directory.exists():
            for f in directory.glob(pattern):
                if f.is_file() and f not in seen:
                    log_files.append(f)
                    seen.add(f)

    return log_files


def get_total_size(files: list[Path]) -> int:
    """Get total size of files in bytes."""
    return sum(f.stat().st_size for f in files if f.exists())


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def get_file_age(file: Path) -> timedelta:
    """Get age of file based on modification time."""
    mtime = datetime.fromtimestamp(file.stat().st_mtime)
    return datetime.now() - mtime


def archive_file(file: Path, archive_dir: Path) -> Path:
    """Archive a file with timestamp in filename."""
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Create archive filename with date
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"{file.stem}_{timestamp}{file.suffix}"
    archive_path = archive_dir / archive_name

    # Compress if large, otherwise just move
    if file.stat().st_size > 10 * 1024 * 1024:  # >10MB
        import gzip
        archive_path = archive_path.with_suffix(archive_path.suffix + '.gz')
        with open(file, 'rb') as f_in:
            with gzip.open(archive_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        file.unlink()
    else:
        shutil.move(str(file), str(archive_path))

    return archive_path


def check_status(log_files: list[Path], age_days: int):
    """Display current log status."""
    total_size = get_total_size(log_files)

    print(f"\n{'='*60}")
    print("LOG FILE STATUS")
    print(f"{'='*60}")
    print(f"Total log files: {len(log_files)}")
    print(f"Total size: {format_size(total_size)}")
    print(f"Size threshold: {format_size(DEFAULT_SIZE_MB * 1024 * 1024)}")
    print(f"Age threshold: {age_days} days")
    print(f"{'='*60}\n")

    if log_files:
        print("FILES:")
        for f in sorted(log_files, key=lambda x: x.stat().st_size, reverse=True):
            age = get_file_age(f)
            size = format_size(f.stat().st_size)
            age_str = f"{age.days}d" if age.days > 0 else f"{age.seconds//3600}h"
            old_marker = " [OLD]" if age.days >= age_days else ""
            print(f"  {f.name:<30} {size:>10}  ({age_str}){old_marker}")
    else:
        print("No log files found.")

    print()


def run_archive(age_days: int, size_threshold_mb: int, force: bool = False) -> dict:
    """Run the archive process."""
    log_files = get_log_files()
    total_size = get_total_size(log_files)
    threshold_bytes = size_threshold_mb * 1024 * 1024

    results = {
        "files_checked": len(log_files),
        "total_size_before": total_size,
        "files_archived": [],
        "space_freed": 0,
        "skipped_reason": None
    }

    # Check if we should archive
    if not force and total_size < threshold_bytes:
        results["skipped_reason"] = f"Total size ({format_size(total_size)}) below threshold ({format_size(threshold_bytes)})"
        return results

    # Find old files to archive
    cutoff = datetime.now() - timedelta(days=age_days)

    for f in log_files:
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        if mtime < cutoff:
            file_size = f.stat().st_size
            try:
                archive_path = archive_file(f, ARCHIVE_DIR)
                results["files_archived"].append({
                    "original": str(f),
                    "archived": str(archive_path),
                    "size": file_size
                })
                results["space_freed"] += file_size
                print(f"[ARCHIVED] {f.name} -> {archive_path.name}")
            except Exception as e:
                print(f"[ERROR] Failed to archive {f.name}: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Archive old log files when total size exceeds threshold",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check status only, don't archive"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Archive old files regardless of size threshold"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_AGE_DAYS,
        help=f"Age threshold in days (default: {DEFAULT_AGE_DAYS})"
    )
    parser.add_argument(
        "--size",
        type=int,
        default=DEFAULT_SIZE_MB,
        help=f"Size threshold in MB (default: {DEFAULT_SIZE_MB})"
    )

    args = parser.parse_args()

    log_files = get_log_files()

    if args.check:
        check_status(log_files, args.days)
        return 0

    print(f"[LOG ARCHIVE] Checking {len(log_files)} log files...")
    results = run_archive(args.days, args.size, args.force)

    if results["skipped_reason"]:
        print(f"[SKIPPED] {results['skipped_reason']}")
        return 0

    if results["files_archived"]:
        print(f"\n[COMPLETE] Archived {len(results['files_archived'])} files")
        print(f"[COMPLETE] Space freed: {format_size(results['space_freed'])}")
    else:
        print("[COMPLETE] No files old enough to archive")

    return 0


if __name__ == "__main__":
    sys.exit(main())
