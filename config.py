import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_USER_TOKEN = os.getenv("SLACK_USER_TOKEN")
    SLACK_USER_ID = os.getenv("SLACK_USER_ID")
    NOTIFICATION_CHANNEL_ID = os.getenv("NOTIFICATION_CHANNEL_ID")
    CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "60"))

    @classmethod
    def validate(cls):
        missing = []
        if not cls.SLACK_BOT_TOKEN and not cls.SLACK_USER_TOKEN:
            missing.append("SLACK_BOT_TOKEN or SLACK_USER_TOKEN")
        if not cls.SLACK_USER_ID:
            missing.append("SLACK_USER_ID")
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")
