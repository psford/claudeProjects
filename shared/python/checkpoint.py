#!/usr/bin/env python3
"""
Checkpoint System - Graceful Session State Management

Helps Claude save incremental state during long sessions to enable graceful
recovery if the session ends unexpectedly or approaches token limits.

Usage:
    python helpers/checkpoint.py save "Brief description of current state"
    python helpers/checkpoint.py status
    python helpers/checkpoint.py clear

The checkpoint is stored in sessionState.md under a dedicated section.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# shared/python/ is 2 levels deep from claudeProjects/
PROJECT_ROOT = Path(__file__).parent.parent.parent
SESSION_STATE_FILE = PROJECT_ROOT / "sessionState.md"

CHECKPOINT_HEADER = "## Checkpoint (Auto-saved)"
CHECKPOINT_MARKER_START = "<!-- CHECKPOINT_START -->"
CHECKPOINT_MARKER_END = "<!-- CHECKPOINT_END -->"


def get_checkpoint_block(description: str, todos: list[str] = None) -> str:
    """Generate a checkpoint block with timestamp and state."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    block = f"""{CHECKPOINT_MARKER_START}
{CHECKPOINT_HEADER}

**Last checkpoint:** {timestamp}

**Current state:** {description}
"""

    if todos:
        block += "\n**Active tasks:**\n"
        for todo in todos:
            block += f"- {todo}\n"

    block += f"""
**Recovery:** If session ended unexpectedly, this checkpoint indicates where work was interrupted. Resume from here.

{CHECKPOINT_MARKER_END}"""

    return block


def read_session_state() -> str:
    """Read the current session state file."""
    if SESSION_STATE_FILE.exists():
        return SESSION_STATE_FILE.read_text(encoding="utf-8")
    return ""


def write_session_state(content: str):
    """Write updated session state file."""
    SESSION_STATE_FILE.write_text(content, encoding="utf-8")


def save_checkpoint(description: str, todos: list[str] = None):
    """Save a checkpoint to sessionState.md."""
    content = read_session_state()
    checkpoint_block = get_checkpoint_block(description, todos)

    # Remove existing checkpoint if present
    if CHECKPOINT_MARKER_START in content:
        start_idx = content.find(CHECKPOINT_MARKER_START)
        end_idx = content.find(CHECKPOINT_MARKER_END)
        if end_idx != -1:
            end_idx += len(CHECKPOINT_MARKER_END)
            content = content[:start_idx] + content[end_idx:]
            content = content.strip()

    # Insert checkpoint after the header (after first ---)
    lines = content.split("\n")
    insert_idx = 0
    dash_count = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            dash_count += 1
            if dash_count == 1:
                insert_idx = i + 1
                break

    if insert_idx > 0:
        lines.insert(insert_idx, "")
        lines.insert(insert_idx + 1, checkpoint_block)
        lines.insert(insert_idx + 2, "")
        content = "\n".join(lines)
    else:
        # Fallback: append at end
        content += f"\n\n{checkpoint_block}\n"

    write_session_state(content)
    print(f"[CHECKPOINT] Saved at {datetime.now().strftime('%H:%M:%S')}: {description}")


def show_status():
    """Show current checkpoint status."""
    content = read_session_state()

    if CHECKPOINT_MARKER_START not in content:
        print("[CHECKPOINT] No active checkpoint found.")
        return

    start_idx = content.find(CHECKPOINT_MARKER_START)
    end_idx = content.find(CHECKPOINT_MARKER_END)

    if end_idx != -1:
        checkpoint = content[start_idx:end_idx + len(CHECKPOINT_MARKER_END)]
        # Extract just the readable part
        lines = checkpoint.split("\n")
        for line in lines:
            if line.startswith("**Last checkpoint:**") or \
               line.startswith("**Current state:**") or \
               line.startswith("- "):
                print(line)


def clear_checkpoint():
    """Remove checkpoint from sessionState.md."""
    content = read_session_state()

    if CHECKPOINT_MARKER_START not in content:
        print("[CHECKPOINT] No checkpoint to clear.")
        return

    start_idx = content.find(CHECKPOINT_MARKER_START)
    end_idx = content.find(CHECKPOINT_MARKER_END)

    if end_idx != -1:
        end_idx += len(CHECKPOINT_MARKER_END)
        # Also remove surrounding whitespace
        while end_idx < len(content) and content[end_idx] in "\n\r":
            end_idx += 1
        content = content[:start_idx] + content[end_idx:]
        content = content.strip() + "\n"
        write_session_state(content)
        print("[CHECKPOINT] Cleared.")


def main():
    parser = argparse.ArgumentParser(
        description="Checkpoint system for graceful session state management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Save command
    save_parser = subparsers.add_parser("save", help="Save a checkpoint")
    save_parser.add_argument("description", help="Brief description of current state")
    save_parser.add_argument("--todos", nargs="*", help="List of active tasks")

    # Status command
    subparsers.add_parser("status", help="Show current checkpoint status")

    # Clear command
    subparsers.add_parser("clear", help="Clear the checkpoint")

    args = parser.parse_args()

    if args.command == "save":
        save_checkpoint(args.description, args.todos)
    elif args.command == "status":
        show_status()
    elif args.command == "clear":
        clear_checkpoint()
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
