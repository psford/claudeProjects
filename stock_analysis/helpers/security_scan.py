#!/usr/bin/env python3
"""
Security Scanner Helper

Runs Bandit static analysis on Python code.
Part of the helpers/ tooling for reusable development utilities.

Usage:
    python helpers/security_scan.py [path] [--strict] [--json] [--fix]

Arguments:
    path        Directory or file to scan (default: stock_analysis/)
    --strict    Fail on any issue (default: fail on medium+ severity)
    --json      Output JSON format instead of text
    --fix       Show suggested fixes for issues

Examples:
    python helpers/security_scan.py                    # Scan stock_analysis/
    python helpers/security_scan.py . --strict         # Scan everything, strict mode
    python helpers/security_scan.py --json > report.json  # JSON output

Exit codes:
    0 - No issues found (or only low severity in non-strict mode)
    1 - Security issues found
    2 - Error running scanner
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_bandit(target_path: str, output_format: str = "txt",
               severity_level: str = "medium") -> tuple[int, str]:
    """
    Run Bandit security scanner.

    Args:
        target_path: Directory or file to scan
        output_format: Output format (txt, json, csv, html)
        severity_level: Minimum severity to report (low, medium, high)

    Returns:
        Tuple of (exit_code, output)
    """
    cmd = [
        sys.executable, "-m", "bandit",
        "-r", target_path,
        "-f", output_format,
        "-ll" if severity_level == "medium" else "",  # -ll = medium+, -l = low+
    ]

    # Remove empty strings from command
    cmd = [c for c in cmd if c]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout + result.stderr
    except FileNotFoundError:
        return 2, "Error: Bandit not installed. Run: pip install bandit"


def main():
    parser = argparse.ArgumentParser(
        description="Run Bandit security scanner on Python code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Directory or file to scan (default: current directory)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any issue (including low severity)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show issues, no banner"
    )

    args = parser.parse_args()

    # Validate path exists
    target = Path(args.path)
    if not target.exists():
        print(f"Error: Path not found: {args.path}")
        sys.exit(2)

    # Determine settings
    output_format = "json" if args.json else "txt"
    severity = "low" if args.strict else "medium"

    if not args.quiet and not args.json:
        print("=" * 60)
        print("SECURITY SCAN - Bandit Static Analysis")
        print("=" * 60)
        print(f"Target: {args.path}")
        print(f"Mode: {'Strict (all issues)' if args.strict else 'Standard (medium+ severity)'}")
        print("-" * 60)

    # Run scan
    exit_code, output = run_bandit(str(target), output_format, severity)

    print(output)

    if not args.quiet and not args.json:
        print("-" * 60)
        if exit_code == 0:
            print("[PASS] No security issues found")
        elif exit_code == 1:
            print("[FAIL] Security issues detected - review and fix before merging")
        else:
            print("[ERROR] Scanner error")
        print("=" * 60)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
