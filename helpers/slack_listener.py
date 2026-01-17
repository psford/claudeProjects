#!/usr/bin/env python3
"""
Slack Listener - Background Service

Listens for incoming Slack messages and saves them to slack_inbox.json.
Run this as a background process to enable two-way Claude-user communication.

Usage:
    python helpers/slack_listener.py              # Run in foreground
    python helpers/slack_listener.py --daemon     # Run in background (Windows)
    python helpers/slack_listener.py --check      # Check inbox without starting listener
    python helpers/slack_listener.py --sync       # Fetch missed messages from channel history

The listener saves messages to: slack_inbox.json

Environment:
    SLACK_BOT_TOKEN   Bot OAuth token (xoxb-...)
    SLACK_APP_TOKEN   App-level token for Socket Mode (xapp-...)
    SLACK_CHANNEL_ID  Channel ID to sync history from (optional, for --sync)
"""

import json
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import logging

# Enable debug logging for slack_bolt
logging.basicConfig(level=logging.DEBUG)
slack_logger = logging.getLogger("slack_bolt")

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
INBOX_FILE = PROJECT_ROOT / "slack_inbox.json"
LOG_FILE = PROJECT_ROOT / "slack_listener.log"
LAST_SYNC_FILE = PROJECT_ROOT / "slack_last_sync.txt"

# Default channel for syncing (claude-notifications)
DEFAULT_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "C0A8LB49E1M")


def log(message: str):
    """Write to log file and print."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")


def load_inbox() -> list:
    """Load existing inbox messages."""
    if INBOX_FILE.exists():
        try:
            with open(INBOX_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


def save_inbox(messages: list):
    """Save messages to inbox file."""
    with open(INBOX_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)


def add_message(user: str, channel: str, text: str, timestamp: str):
    """Add a new message to the inbox."""
    inbox = load_inbox()

    message = {
        "id": len(inbox) + 1,
        "user": user,
        "channel": channel,
        "text": text,
        "timestamp": timestamp,
        "received_at": datetime.now().isoformat(),
        "read": False
    }

    inbox.append(message)
    save_inbox(inbox)
    log(f"New message from {user}: {text[:50]}...")

    return message


def get_unread_messages() -> list:
    """Get all unread messages."""
    inbox = load_inbox()
    return [m for m in inbox if not m.get("read", False)]


def mark_all_read():
    """Mark all messages as read."""
    inbox = load_inbox()
    for msg in inbox:
        msg["read"] = True
    save_inbox(inbox)


def clear_inbox():
    """Clear all messages from inbox."""
    save_inbox([])
    log("Inbox cleared")


def get_last_sync_ts() -> str:
    """Get the timestamp of last sync, or None if never synced."""
    if LAST_SYNC_FILE.exists():
        try:
            return LAST_SYNC_FILE.read_text().strip()
        except Exception:
            pass
    return None


def set_last_sync_ts(ts: str):
    """Save the timestamp of last sync."""
    LAST_SYNC_FILE.write_text(ts)


def get_known_timestamps() -> set:
    """Get set of all message timestamps we already have."""
    inbox = load_inbox()
    return {msg.get("timestamp") for msg in inbox if msg.get("timestamp")}


def sync_history(channel_id: str = None, limit: int = 50) -> int:
    """
    Fetch recent channel history and add any missed messages.

    Returns the number of new messages added.
    """
    from slack_sdk import WebClient

    channel_id = channel_id or DEFAULT_CHANNEL_ID
    bot_token = os.getenv("SLACK_BOT_TOKEN")

    if not bot_token:
        log("[ERROR] SLACK_BOT_TOKEN not found")
        return 0

    client = WebClient(token=bot_token)
    known_ts = get_known_timestamps()
    new_count = 0

    try:
        # Fetch recent messages
        log(f"Syncing history from channel {channel_id}...")
        result = client.conversations_history(channel=channel_id, limit=limit)

        messages = result.get("messages", [])
        log(f"Fetched {len(messages)} messages from channel")

        # Process messages (oldest first)
        for msg in reversed(messages):
            # Skip bot messages
            if msg.get("bot_id") or msg.get("subtype") == "bot_message":
                continue

            ts = msg.get("ts", "")

            # Skip if we already have this message
            if ts in known_ts:
                continue

            user_id = msg.get("user", "unknown")
            text = msg.get("text", "")

            # Get user display name
            try:
                user_info = client.users_info(user=user_id)
                user_name = user_info["user"].get("real_name") or user_info["user"].get("name") or user_id
            except Exception:
                user_name = user_id

            # Add to inbox
            add_message(
                user=user_name,
                channel=f"#{channel_id}",
                text=text,
                timestamp=ts
            )
            known_ts.add(ts)
            new_count += 1

        # Update last sync timestamp
        if messages:
            latest_ts = messages[0].get("ts", "")
            if latest_ts:
                set_last_sync_ts(latest_ts)

        log(f"Sync complete: {new_count} new messages added")
        return new_count

    except Exception as e:
        log(f"[ERROR] Failed to sync history: {e}")
        return 0


def check_inbox():
    """Display inbox status."""
    inbox = load_inbox()
    unread = get_unread_messages()

    print(f"\n{'='*60}")
    print("SLACK INBOX STATUS")
    print(f"{'='*60}")
    print(f"Total messages: {len(inbox)}")
    print(f"Unread messages: {len(unread)}")
    print(f"{'='*60}\n")

    if unread:
        print("UNREAD MESSAGES:\n")
        for msg in unread:
            print(f"  [{msg['id']}] From: {msg['user']}")
            print(f"      Channel: {msg['channel']}")
            print(f"      Time: {msg['received_at']}")
            print(f"      Message: {msg['text']}")
            print()
    else:
        print("No unread messages.\n")


def create_app() -> App:
    """Create and configure the Slack Bolt app."""
    bot_token = os.getenv("SLACK_BOT_TOKEN")

    if not bot_token:
        raise ValueError("SLACK_BOT_TOKEN not found in environment")

    app = App(token=bot_token)
    log("App created with bot token")

    # Listen for messages in channels the bot is in
    @app.event("message")
    def handle_message(event, say, client):
        """Handle incoming messages."""
        # Ignore bot messages (including our own)
        if event.get("bot_id") or event.get("subtype") == "bot_message":
            return

        user_id = event.get("user", "unknown")
        channel_id = event.get("channel", "unknown")
        text = event.get("text", "")
        ts = event.get("ts", "")

        # Get user info for display name
        try:
            user_info = client.users_info(user=user_id)
            user_name = user_info["user"]["real_name"] or user_info["user"]["name"]
        except Exception:
            user_name = user_id

        # Get channel info
        try:
            channel_info = client.conversations_info(channel=channel_id)
            channel_name = channel_info["channel"]["name"]
        except Exception:
            channel_name = channel_id

        # Save the message
        add_message(
            user=user_name,
            channel=f"#{channel_name}",
            text=text,
            timestamp=ts
        )

        # Acknowledge receipt with reaction (cleaner than reply)
        try:
            client.reactions_add(channel=channel_id, timestamp=ts, name="white_check_mark")
        except Exception as e:
            log(f"Failed to add reaction: {e}")

    # Handle app mentions
    @app.event("app_mention")
    def handle_mention(event, say, client):
        """Handle @mentions of the bot."""
        user_id = event.get("user", "unknown")
        channel_id = event.get("channel", "unknown")
        text = event.get("text", "")
        ts = event.get("ts", "")

        # Get user info
        try:
            user_info = client.users_info(user=user_id)
            user_name = user_info["user"]["real_name"] or user_info["user"]["name"]
        except Exception:
            user_name = user_id

        # Get channel info
        try:
            channel_info = client.conversations_info(channel=channel_id)
            channel_name = channel_info["channel"]["name"]
        except Exception:
            channel_name = channel_id

        # Save the message
        add_message(
            user=user_name,
            channel=f"#{channel_name}",
            text=text,
            timestamp=ts
        )

        # Acknowledge with reaction
        try:
            client.reactions_add(channel=channel_id, timestamp=ts, name="white_check_mark")
        except Exception as e:
            log(f"Failed to add reaction: {e}")

    return app


def main():
    parser = argparse.ArgumentParser(
        description="Slack message listener for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check inbox status without starting listener"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all messages from inbox"
    )
    parser.add_argument(
        "--mark-read",
        action="store_true",
        help="Mark all messages as read"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as background process (Windows)"
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Fetch missed messages from channel history"
    )
    parser.add_argument(
        "--no-sync",
        action="store_true",
        help="Skip history sync on startup"
    )

    args = parser.parse_args()

    # Handle check/clear modes
    if args.check:
        check_inbox()
        return 0

    if args.clear:
        clear_inbox()
        print("Inbox cleared.")
        return 0

    if args.mark_read:
        mark_all_read()
        print("All messages marked as read.")
        return 0

    if args.sync:
        new_count = sync_history()
        print(f"Sync complete: {new_count} new messages added")
        check_inbox()
        return 0

    # Validate tokens
    app_token = os.getenv("SLACK_APP_TOKEN")
    bot_token = os.getenv("SLACK_BOT_TOKEN")

    if not app_token:
        print("[ERROR] SLACK_APP_TOKEN not found in .env")
        return 1

    if not bot_token:
        print("[ERROR] SLACK_BOT_TOKEN not found in .env")
        return 1

    # Create app
    try:
        app = create_app()
    except Exception as e:
        print(f"[ERROR] Failed to create app: {e}")
        return 1

    # Sync history on startup to catch missed messages
    if not args.no_sync:
        log("Syncing channel history to catch missed messages...")
        new_count = sync_history()
        if new_count > 0:
            log(f"Found {new_count} missed messages")

    # Start listener
    log("Starting Slack listener...")
    log(f"Inbox file: {INBOX_FILE}")
    log("Listening for messages. Press Ctrl+C to stop.")

    try:
        handler = SocketModeHandler(app, app_token)
        handler.start()
    except KeyboardInterrupt:
        log("Listener stopped by user.")
        return 0
    except Exception as e:
        log(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
