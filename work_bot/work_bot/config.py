import os
from zoneinfo import ZoneInfo

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "work_time.sqlite3")
DEFAULT_TZ = os.getenv("DEFAULT_TZ", "Europe/Moscow")
WEEKLY_REPORT_DAY = os.getenv("WEEKLY_REPORT_DAY", "sun")
WEEKLY_REPORT_HOUR = int(os.getenv("WEEKLY_REPORT_HOUR", "20"))

if not BOT_TOKEN:
    raise RuntimeError("Set BOT_TOKEN environment variable")

DEFAULT_ZONEINFO = ZoneInfo(DEFAULT_TZ)
