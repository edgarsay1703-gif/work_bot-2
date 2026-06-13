from aiogram import Router, types
from aiogram.filters import Command
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import database

router = Router()

@router.message(Command("tz"))
async def tz_cmd(message: types.Message):
    user_id = message.from_user.id
    database.ensure_user(user_id)
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Напиши так: /tz Europe/Moscow")
        return
    timezone = parts[1].strip()
    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        await message.answer("Не знаю такой часовой пояс. Пример: /tz Europe/Moscow")
        return
    database.set_user_timezone(user_id, timezone)
    await message.answer(f"✅ Часовой пояс установлен: <b>{timezone}</b>", parse_mode="HTML")
