from datetime import time, timedelta, datetime

import database
import utils

def seconds_by_day(user_id: int, start_local: datetime, days: int) -> list[int]:
    tz = start_local.tzinfo
    result = [0] * days
    end_local = start_local + timedelta(days=days)
    start_utc = utils.to_utc_iso(start_local)
    end_utc = utils.to_utc_iso(end_local)
    rows = database.get_sessions_in_range(user_id, start_utc, end_utc)

    for started_raw, ended_raw in rows:
        started = utils.from_iso(started_raw).astimezone(tz)
        ended = (
            utils.from_iso(ended_raw).astimezone(tz)
            if ended_raw
            else utils.now_utc().astimezone(tz)
        )
        clipped_start = max(started, start_local)
        clipped_end = min(ended, end_local)
        cursor = clipped_start
        while cursor < clipped_end:
            day_index = (cursor.date() - start_local.date()).days
            next_day = datetime.combine(
                cursor.date() + timedelta(days=1), time.min, tzinfo=tz
            )
            segment_end = min(next_day, clipped_end)
            if 0 <= day_index < days:
                result[day_index] += int((segment_end - cursor).total_seconds())
            cursor = segment_end
    return result

def render_bar(seconds: int, max_seconds: int, width: int = 12) -> str:
    filled = round((seconds / max_seconds) * width) if max_seconds > 0 else 0
    return "█" * filled + "░" * (width - filled)

def render_week_report(user_id: int) -> str:
    tz = database.get_user_tz(user_id)
    local_now = utils.now_utc().astimezone(tz)
    start, _ = utils.week_bounds(local_now)
    values = seconds_by_day(user_id, start, 7)
    max_value = max(values) if values else 0
    day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    total = sum(values)
    lines = ["📊 <b>Статистика за текущую неделю</b>", ""]
    for i, secs in enumerate(values):
        date_label = (start + timedelta(days=i)).strftime("%d.%m")
        bar = render_bar(secs, max_value)
        lines.append(f"{day_names[i]} {date_label} | {bar} | {utils.format_duration(secs)}")
    lines += ["", f"<b>Итого: {utils.format_duration(total)}</b>"]
    return "\n".join(lines)

def render_month_report(user_id: int) -> str:
    tz = database.get_user_tz(user_id)
    local_now = utils.now_utc().astimezone(tz)
    start, end = utils.month_bounds(local_now)
    days = (end.date() - start.date()).days
    values = seconds_by_day(user_id, start, days)
    total = sum(values)
    worked_days = sum(1 for s in values if s > 0)
    avg = total // worked_days if worked_days else 0
    return (
        "📅 <b>Статистика за текущий месяц</b>\n\n"
        f"Всего: <b>{utils.format_duration(total)}</b>\n"
        f"Рабочих дней: {worked_days}\n"
        f"Среднее за рабочий день: {utils.format_duration(avg)}"
    )
