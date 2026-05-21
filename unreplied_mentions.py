#!/usr/bin/env python3
"""
Find unreplied mentions in Slack.
"""
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from slack_client import SlackClient
from config import Config


@dataclass
class UnrepliedMention:
    channel_id: str
    channel_name: str
    message_ts: str
    thread_ts: str | None
    sender_id: str
    sender_name: str
    text: str
    timestamp: datetime
    permalink: str | None


def find_unreplied_mentions(days: int = 7) -> list[UnrepliedMention]:
    """
    Find all mentions of the user that haven't been replied to.

    Args:
        days: Number of days to look back (default: 7)

    Returns:
        List of UnrepliedMention objects
    """
    Config.validate()
    client = SlackClient()
    user_id = Config.SLACK_USER_ID
    since = datetime.now() - timedelta(days=days)

    mention_pattern = re.compile(rf"<@{user_id}>")
    unreplied = []
    user_cache = {}

    channels = client.get_channels()

    for channel in channels:
        channel_id = channel["id"]
        channel_name = channel.get("name", "DM")

        messages = client.get_messages_since(channel_id, since)

        for msg in messages:
            if msg.get("user") == user_id:
                continue

            text = msg.get("text", "")
            if not mention_pattern.search(text):
                continue

            msg_ts = msg["ts"]
            thread_ts = msg.get("thread_ts")

            has_reply = False

            if thread_ts:
                replies = client.get_thread_replies(channel_id, thread_ts)
                for reply in replies:
                    if reply.get("user") == user_id and float(reply["ts"]) > float(msg_ts):
                        has_reply = True
                        break
            else:
                thread_replies = client.get_thread_replies(channel_id, msg_ts)
                for reply in thread_replies:
                    if reply.get("user") == user_id:
                        has_reply = True
                        break

            if has_reply:
                continue

            sender_id = msg.get("user", "unknown")
            if sender_id not in user_cache:
                user_info = client.get_user_info(sender_id)
                user_cache[sender_id] = user_info.get("real_name", sender_id) if user_info else sender_id

            permalink = client.get_permalink(channel_id, msg_ts)

            unreplied.append(UnrepliedMention(
                channel_id=channel_id,
                channel_name=channel_name,
                message_ts=msg_ts,
                thread_ts=thread_ts,
                sender_id=sender_id,
                sender_name=user_cache[sender_id],
                text=text[:200] + "..." if len(text) > 200 else text,
                timestamp=datetime.fromtimestamp(float(msg_ts)),
                permalink=permalink,
            ))

    unreplied.sort(key=lambda x: x.timestamp, reverse=True)
    return unreplied


def format_mentions_report(mentions: list[UnrepliedMention]) -> str:
    """Format unreplied mentions as a readable report."""
    if not mentions:
        return "未返信のメンションはありません。"

    lines = [f"未返信メンション: {len(mentions)}件\n"]

    for i, m in enumerate(mentions, 1):
        date_str = m.timestamp.strftime("%Y-%m-%d %H:%M")
        lines.append(f"{i}. [{date_str}] #{m.channel_name}")
        lines.append(f"   From: {m.sender_name}")
        lines.append(f"   {m.text}")
        if m.permalink:
            lines.append(f"   Link: {m.permalink}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    mentions = find_unreplied_mentions(days=7)
    print(format_mentions_report(mentions))
