#!/usr/bin/env python3
"""
ZAP Security Scanner - DAST Helper

Runs OWASP ZAP security scans against web applications using Docker.

Usage:
    python helpers/zap_scan.py                      # Scan localhost:8501 (Streamlit default)
    python helpers/zap_scan.py --url http://localhost:3000
    python helpers/zap_scan.py --full               # Full scan (slower, more thorough)
    python helpers/zap_scan.py --api                # API scan mode

Scan Types:
    baseline (default): Quick passive scan (~1-2 minutes)
    full: Active scanning with attack simulation (~10+ minutes)
    api: Optimized for REST/GraphQL APIs

Requirements:
    - Docker Desktop running
    - ZAP image: docker pull zaproxy/zap-stable
"""

import argparse
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# Docker executable path (Windows)
DOCKER_PATHS = [
    r"C:\Program Files\Docker\Docker\resources\bin\docker.exe",
    "docker"  # Fallback to PATH
]

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "security_reports"


def find_docker():
    """Find Docker executable."""
    for path in DOCKER_PATHS:
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return path
        except FileNotFoundError:
            continue
    return None


def ensure_reports_dir():
    """Create reports directory if it doesn't exist."""
    REPORTS_DIR.mkdir(exist_ok=True)
    return REPORTS_DIR


def run_zap_scan(url: str, scan_type: str = "baseline", docker_path: str = "docker"):
    """
    Run ZAP scan against target URL.

    Args:
        url: Target URL to scan
        scan_type: One of 'baseline', 'full', 'api'
        docker_path: Path to docker executable
    """
    reports_dir = ensure_reports_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"zap_{scan_type}_{timestamp}"

    # Map scan types to ZAP scripts
    scan_scripts = {
        "baseline": "zap-baseline.py",
        "full": "zap-full-scan.py",
        "api": "zap-api-scan.py"
    }

    script = scan_scripts.get(scan_type, "zap-baseline.py")

    # Convert Windows path to Docker-compatible path
    reports_path_docker = str(reports_dir).replace("\\", "/")
    if reports_path_docker[1] == ":":
        # Convert C:\path to /c/path for Docker
        reports_path_docker = "/" + reports_path_docker[0].lower() + reports_path_docker[2:]

    print(f"\n{'='*60}")
    print(f"OWASP ZAP {scan_type.upper()} SCAN")
    print(f"{'='*60}")
    print(f"Target: {url}")
    print(f"Type: {scan_type}")
    print(f"Report: {reports_dir / report_name}.html")
    print(f"{'='*60}\n")

    # Build Docker command
    cmd = [
        docker_path, "run", "--rm",
        "-v", f"{reports_path_docker}:/zap/wrk:rw",
        "-t", "zaproxy/zap-stable",
        script,
        "-t", url,
        "-r", f"{report_name}.html",
        "-J", f"{report_name}.json"
    ]

    # Add scan-specific options
    if scan_type == "baseline":
        cmd.extend(["-I"])  # Don't fail on warnings
    elif scan_type == "api":
        cmd.extend(["-f", "openapi"])  # Assume OpenAPI format

    print(f"Running: {' '.join(cmd)}\n")

    try:
        # Set environment to include Docker path
        env = os.environ.copy()
        docker_bin_dir = str(Path(docker_path).parent)
        env["PATH"] = docker_bin_dir + os.pathsep + env.get("PATH", "")

        result = subprocess.run(
            cmd,
            env=env,
            timeout=1800  # 30 minute timeout
        )

        print(f"\n{'='*60}")
        if result.returncode == 0:
            print("SCAN COMPLETED SUCCESSFULLY")
        elif result.returncode == 1:
            print("SCAN COMPLETED WITH WARNINGS")
        elif result.returncode == 2:
            print("SCAN COMPLETED WITH FAILURES")
        else:
            print(f"SCAN COMPLETED WITH CODE {result.returncode}")

        # Check for report files
        html_report = reports_dir / f"{report_name}.html"
        json_report = reports_dir / f"{report_name}.json"

        print(f"{'='*60}")
        if html_report.exists():
            print(f"HTML Report: {html_report}")
        if json_report.exists():
            print(f"JSON Report: {json_report}")
        print(f"{'='*60}\n")

        return result.returncode

    except subprocess.TimeoutExpired:
        print("\n[ERROR] Scan timed out after 30 minutes")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Scan failed: {e}")
        return 1


def check_target_reachable(url: str):
    """Check if target URL is reachable."""
    import urllib.request
    import urllib.error

    try:
        urllib.request.urlopen(url, timeout=5)
        return True
    except urllib.error.URLError:
        return False
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run OWASP ZAP security scans via Docker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--url", "-u",
        default="http://host.docker.internal:8501",
        help="Target URL to scan (default: http://host.docker.internal:8501 for Streamlit)"
    )
    parser.add_argument(
        "--baseline", "-b",
        action="store_true",
        help="Run baseline scan (default, quick passive scan)"
    )
    parser.add_argument(
        "--full", "-f",
        action="store_true",
        help="Run full scan (slower, active testing)"
    )
    parser.add_argument(
        "--api", "-a",
        action="store_true",
        help="Run API scan (for REST/GraphQL endpoints)"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check if Docker and ZAP are available"
    )

    args = parser.parse_args()

    # Find Docker
    docker_path = find_docker()
    if not docker_path:
        print("[ERROR] Docker not found. Please ensure Docker Desktop is running.")
        print("Install with: winget install Docker.DockerDesktop")
        return 1

    print(f"[OK] Docker found: {docker_path}")

    # Check ZAP image
    result = subprocess.run(
        [docker_path, "images", "-q", "zaproxy/zap-stable"],
        capture_output=True,
        text=True
    )
    if not result.stdout.strip():
        print("[WARNING] ZAP image not found. Pulling...")
        subprocess.run([docker_path, "pull", "zaproxy/zap-stable"])
    else:
        print("[OK] ZAP image available")

    if args.check_only:
        print("\n[OK] All prerequisites met. Ready to scan.")
        return 0

    # Determine scan type
    if args.full:
        scan_type = "full"
    elif args.api:
        scan_type = "api"
    else:
        scan_type = "baseline"

    # Note about Docker networking
    url = args.url
    if "localhost" in url or "127.0.0.1" in url:
        # Replace localhost with Docker's host reference
        url = url.replace("localhost", "host.docker.internal")
        url = url.replace("127.0.0.1", "host.docker.internal")
        print(f"[NOTE] Using Docker host reference: {url}")

    # Run scan
    return run_zap_scan(url, scan_type, docker_path)


if __name__ == "__main__":
    sys.exit(main())
