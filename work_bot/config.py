import os
from zoneinfo import ZoneInfo

BOT_TOKEN = os.getenv("BOT_TOKEN")

# На Render диск монтируется в /data — используем его для БД
_default_db = os.path.join(os.getenv("RENDER_DISK_MOUNT", "/data"), "work_time.sqlite3")
DB_PATH = os.getenv("DB_PATH", _default_db)

DEFAULT_TZ = os.getenv("DEFAULT_TZ", "Europe/Moscow")
WEEKLY_REPORT_DAY = os.getenv("WEEKLY_REPORT_DAY", "sun")
WEEKLY_REPORT_HOUR = int(os.getenv("WEEKLY_REPORT_HOUR", "20"))

if not BOT_TOKEN:
    raise RuntimeError("Set BOT_TOKEN environment variable")

DEFAULT_ZONEINFO = ZoneInfo(DEFAULT_TZ)
