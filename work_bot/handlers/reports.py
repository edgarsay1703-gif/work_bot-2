from aiogram import Router, types
from aiogram.filters import Command
import database
import report_builder

router = Router()

@router.message(Command("week"))
async def week_cmd(message: types.Message):
    database.ensure_user(message.from_user.id)
    await message.answer(
        report_builder.render_week_report(message.from_user.id),
        parse_mode="HTML",
    )

@router.message(Command("month"))
async def month_cmd(message: types.Message):
    database.ensure_user(message.from_user.id)
    await message.answer(
        report_builder.render_month_report(message.from_user.id),
        parse_mode="HTML",
    )
