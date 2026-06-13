from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc

def now_utc() -> datetime:
    """Возвращает текущее время UTC (timezone-aware). Заменяет устаревший utcnow()."""
    return datetime.now(UTC)

def to_utc_iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat()

def from_iso(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    # Если нет tzinfo — считаем UTC (старые записи в БД)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt

def format_duration(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours} ч {minutes:02d} мин"

def week_bounds(local_now: datetime) -> tuple[datetime, datetime]:
    start = datetime.combine(
        (local_now - timedelta(days=local_now.weekday())).date(),
        time.min,
        tzinfo=local_now.tzinfo,
    )
    end = start + timedelta(days=7)
    return start, end

def month_bounds(local_now: datetime) -> tuple[datetime, datetime]:
    start = datetime(local_now.year, local_now.month, 1, tzinfo=local_now.tzinfo)
    if local_now.month == 12:
        end = datetime(local_now.year + 1, 1, 1, tzinfo=local_now.tzinfo)
    else:
        end = datetime(local_now.year, local_now.month + 1, 1, tzinfo=local_now.tzinfo)
    return start, end
