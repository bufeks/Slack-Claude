#!/usr/bin/env python3
"""
Slack Bot that periodically checks for unreplied mentions and sends notifications.
"""
import signal
import sys
import time

import schedule

from config import Config
from slack_client import SlackClient
from unreplied_mentions import find_unreplied_mentions


def create_notification_blocks(mentions):
    """Create Slack Block Kit blocks for notification."""
    if not mentions:
        return None

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"未返信メンション: {len(mentions)}件",
            }
        },
        {"type": "divider"},
    ]

    for m in mentions[:10]:
        date_str = m.timestamp.strftime("%m/%d %H:%M")
        text = f"*#{m.channel_name}* - {date_str}\n"
        text += f"From: {m.sender_name}\n"
        text += f">{m.text[:100]}{'...' if len(m.text) > 100 else ''}"

        block = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": text},
        }

        if m.permalink:
            block["accessory"] = {
                "type": "button",
                "text": {"type": "plain_text", "text": "開く"},
                "url": m.permalink,
            }

        blocks.append(block)

    if len(mentions) > 10:
        blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"他 {len(mentions) - 10}件..."}
            ]
        })

    return blocks


def check_and_notify():
    """Check for unreplied mentions and send notification."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking for unreplied mentions...")

    try:
        mentions = find_unreplied_mentions(days=7)

        if not mentions:
            print("No unreplied mentions found.")
            return

        print(f"Found {len(mentions)} unreplied mentions.")

        if Config.NOTIFICATION_CHANNEL_ID:
            client = SlackClient()
            blocks = create_notification_blocks(mentions)
            client.send_message(
                channel_id=Config.NOTIFICATION_CHANNEL_ID,
                text=f"未返信メンション: {len(mentions)}件",
                blocks=blocks,
            )
            print("Notification sent.")
        else:
            print("No notification channel configured. Printing to stdout:")
            for m in mentions:
                print(f"  - [{m.timestamp}] #{m.channel_name} from {m.sender_name}")

    except Exception as e:
        print(f"Error: {e}")


def run_bot():
    """Run the bot with scheduled checks."""
    Config.validate()

    print(f"Starting Slack Unreplied Mentions Bot")
    print(f"Check interval: {Config.CHECK_INTERVAL_MINUTES} minutes")
    print(f"Monitoring user: {Config.SLACK_USER_ID}")
    print("-" * 40)

    check_and_notify()

    schedule.every(Config.CHECK_INTERVAL_MINUTES).minutes.do(check_and_notify)

    def signal_handler(sig, frame):
        print("\nShutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    run_bot()
