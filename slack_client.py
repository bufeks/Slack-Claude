from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from config import Config


class SlackClient:
    def __init__(self):
        token = Config.SLACK_USER_TOKEN or Config.SLACK_BOT_TOKEN
        self.client = WebClient(token=token)
        self.user_id = Config.SLACK_USER_ID

    def get_channels(self):
        """Get all channels the user is a member of."""
        channels = []
        cursor = None
        while True:
            response = self.client.conversations_list(
                types="public_channel,private_channel,mpim,im",
                limit=200,
                cursor=cursor,
            )
            channels.extend(response["channels"])
            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        return channels

    def get_messages_since(self, channel_id: str, since: datetime):
        """Get messages from a channel since a given time."""
        messages = []
        oldest = str(since.timestamp())
        cursor = None
        try:
            while True:
                response = self.client.conversations_history(
                    channel=channel_id,
                    oldest=oldest,
                    limit=200,
                    cursor=cursor,
                )
                messages.extend(response["messages"])
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
        except SlackApiError as e:
            if e.response["error"] == "not_in_channel":
                return []
            raise
        return messages

    def get_thread_replies(self, channel_id: str, thread_ts: str):
        """Get all replies in a thread."""
        try:
            response = self.client.conversations_replies(
                channel=channel_id,
                ts=thread_ts,
                limit=200,
            )
            return response["messages"]
        except SlackApiError:
            return []

    def get_user_info(self, user_id: str):
        """Get user information."""
        try:
            response = self.client.users_info(user=user_id)
            return response["user"]
        except SlackApiError:
            return None

    def get_channel_info(self, channel_id: str):
        """Get channel information."""
        try:
            response = self.client.conversations_info(channel=channel_id)
            return response["channel"]
        except SlackApiError:
            return None

    def send_message(self, channel_id: str, text: str, blocks=None):
        """Send a message to a channel."""
        return self.client.chat_postMessage(
            channel=channel_id,
            text=text,
            blocks=blocks,
        )

    def get_permalink(self, channel_id: str, message_ts: str):
        """Get permalink for a message."""
        try:
            response = self.client.chat_getPermalink(
                channel=channel_id,
                message_ts=message_ts,
            )
            return response["permalink"]
        except SlackApiError:
            return None
