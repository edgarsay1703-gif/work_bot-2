import logging
from aiogram import Router, types
from aiogram.filters import Command
import database
import utils

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("in"))
async def in_cmd(message: types.Message):
    user_id = message.from_user.id
    database.ensure_user(user_id)
    active = database.get_active_session(user_id)
    if active:
        await message.answer("Ты уже отмечен как пришедший. Сначала нажми /out.")
        return
    started_utc = utils.to_utc_iso(utils.now_utc())
    database.start_session(user_id, started_utc)
    local_time = utils.now_utc().astimezone(database.get_user_tz(user_id)).strftime("%H:%M")
    await message.answer(f"✅ Приход записан: <b>{local_time}</b>", parse_mode="HTML")

@router.message(Command("out"))
async def out_cmd(message: types.Message):
    user_id = message.from_user.id
    database.ensure_user(user_id)
    active = database.get_active_session(user_id)
    if not active:
        await message.answer("Сейчас нет открытой смены. Сначала нажми /in.")
        return
    session_id, started_raw = active["id"], active["started_at"]
    ended_at = utils.to_utc_iso(utils.now_utc())
    database.close_session(session_id, ended_at)
    duration = int((utils.from_iso(ended_at) - utils.from_iso(started_raw)).total_seconds())
    local_time = utils.now_utc().astimezone(database.get_user_tz(user_id)).strftime("%H:%M")
    await message.answer(
        f"🏁 Уход записан: <b>{local_time}</b>\nЗа смену: <b>{utils.format_duration(duration)}</b>",
        parse_mode="HTML",
    )

@router.message(Command("status"))
async def status_cmd(message: types.Message):
    user_id = message.from_user.id
    database.ensure_user(user_id)
    active = database.get_active_session(user_id)
    if not active:
        await message.answer("Сейчас ты не на работе по данным бота.")
        return
    started_raw = active["started_at"]
    tz = database.get_user_tz(user_id)
    started = utils.from_iso(started_raw).astimezone(tz)
    duration = int((utils.now_utc().astimezone(tz) - started).total_seconds())
    await message.answer(
        f"🟢 На работе с <b>{started.strftime('%H:%M')}</b>\n"
        f"Прошло: <b>{utils.format_duration(duration)}</b>",
        parse_mode="HTML",
    )
