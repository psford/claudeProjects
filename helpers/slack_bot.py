#!/usr/bin/env python3
"""
Slack Bot Manager - Async Message Handling

Manages two independent background services:
1. slack_listener.py - Receives messages, saves to inbox, adds "eyes" reaction
2. slack_acknowledger.py - Watches for read messages, adds "checkmark" reaction

Usage:
    python helpers/slack_bot.py start     # Start both services
    python helpers/slack_bot.py stop      # Stop both services
    python helpers/slack_bot.py status    # Check service status
    python helpers/slack_bot.py restart   # Restart both services

The services run completely independently, allowing message acknowledgment
to happen async from any other shell processes.
"""

import subprocess
import sys
import os
import signal
import json
import time
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
HELPERS_DIR = PROJECT_ROOT / "helpers"
PID_FILE = PROJECT_ROOT / "slack_bot_pids.json"


def get_python_path() -> str:
    """Get the Python executable path."""
    return sys.executable


def load_pids() -> dict:
    """Load saved PIDs."""
    if PID_FILE.exists():
        try:
            with open(PID_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_pids(pids: dict):
    """Save PIDs to file."""
    pids["updated_at"] = datetime.now().isoformat()
    with open(PID_FILE, "w") as f:
        json.dump(pids, f, indent=2)


def is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running."""
    if pid is None:
        return False
    try:
        if sys.platform == "win32":
            # Windows: use tasklist
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True,
                text=True
            )
            return str(pid) in result.stdout
        else:
            # Unix: send signal 0 to check
            os.kill(pid, 0)
            return True
    except (OSError, subprocess.SubprocessError):
        return False


def start_service(name: str, script: str, args: list = None) -> int:
    """Start a background service. Returns PID."""
    python = get_python_path()
    script_path = HELPERS_DIR / script
    cmd = [python, str(script_path)] + (args or [])

    if sys.platform == "win32":
        # Windows: use CREATE_NEW_PROCESS_GROUP and detached
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
            start_new_session=True
        )
    else:
        # Unix: use nohup-style
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

    print(f"  Started {name} (PID: {process.pid})")
    return process.pid


def stop_service(name: str, pid: int) -> bool:
    """Stop a service by PID. Returns True if stopped."""
    if pid is None:
        return False

    try:
        if sys.platform == "win32":
            # Windows: use taskkill
            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                capture_output=True,
                check=True
            )
        else:
            # Unix: send SIGTERM
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.5)
            # Force kill if still running
            if is_process_running(pid):
                os.kill(pid, signal.SIGKILL)

        print(f"  Stopped {name} (PID: {pid})")
        return True
    except Exception as e:
        print(f"  Failed to stop {name}: {e}")
        return False


def start_bot():
    """Start both services."""
    print("Starting Slack bot services...")

    pids = {}

    # Start listener (poll mode, 15s interval)
    pids["listener"] = start_service(
        "Listener",
        "slack_listener.py",
        ["--poll", "-i", "15"]
    )

    # Start acknowledger (5s interval)
    pids["acknowledger"] = start_service(
        "Acknowledger",
        "slack_acknowledger.py",
        ["-i", "5"]
    )

    save_pids(pids)
    print("\nBoth services started. Use 'python helpers/slack_bot.py status' to check.")


def stop_bot():
    """Stop both services."""
    print("Stopping Slack bot services...")

    pids = load_pids()

    if pids.get("listener"):
        stop_service("Listener", pids["listener"])

    if pids.get("acknowledger"):
        stop_service("Acknowledger", pids["acknowledger"])

    # Clear PID file
    if PID_FILE.exists():
        PID_FILE.unlink()

    print("\nAll services stopped.")


def show_status():
    """Show service status."""
    pids = load_pids()

    print(f"\n{'='*50}")
    print("SLACK BOT STATUS")
    print(f"{'='*50}")

    listener_pid = pids.get("listener")
    listener_running = is_process_running(listener_pid)
    print(f"Listener:     {'RUNNING' if listener_running else 'STOPPED'} (PID: {listener_pid or 'N/A'})")

    ack_pid = pids.get("acknowledger")
    ack_running = is_process_running(ack_pid)
    print(f"Acknowledger: {'RUNNING' if ack_running else 'STOPPED'} (PID: {ack_pid or 'N/A'})")

    updated = pids.get("updated_at", "Unknown")
    print(f"\nLast updated: {updated}")
    print(f"{'='*50}\n")

    # Also show inbox status
    inbox_file = PROJECT_ROOT / "slack_inbox.json"
    if inbox_file.exists():
        try:
            with open(inbox_file, "r") as f:
                inbox = json.load(f)
            unread = sum(1 for m in inbox if not m.get("read", False))
            print(f"Inbox: {len(inbox)} messages ({unread} unread)")
        except Exception:
            pass


def restart_bot():
    """Restart both services."""
    stop_bot()
    time.sleep(1)
    start_bot()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    command = sys.argv[1].lower()

    if command == "start":
        start_bot()
    elif command == "stop":
        stop_bot()
    elif command == "status":
        show_status()
    elif command == "restart":
        restart_bot()
    else:
        print(f"Unknown command: {command}")
        print("Usage: slack_bot.py [start|stop|status|restart]")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
