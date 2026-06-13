from aiogram import Router, types
from aiogram.filters import Command
import database

router = Router()

@router.message(Command("start"))
async def start_cmd(message: types.Message):
    database.ensure_user(message.from_user.id)
    await message.answer(
        "Привет! Я помогу учитывать рабочее время.\n\n"
        "<b>Команды:</b>\n"
        "/in — отметить приход\n"
        "/out — отметить уход\n"
        "/status — текущий статус\n"
        "/week — график и итог за неделю\n"
        "/month — итог за месяц\n"
        "/tz Europe/Moscow — установить часовой пояс",
        parse_mode="HTML",
    )
