import asyncio
import logging
import os
import threading

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from flask import Flask

import config
import database
import report_builder
from handlers import start, work, reports, settings

# ── Логирование ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Flask healthcheck (Render требует открытый порт) ─────────────────────────
flask_app = Flask(__name__)

@flask_app.route("/")
@flask_app.route("/health")
def health_check():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port, use_reloader=False)

# ── Бот ──────────────────────────────────────────────────────────────────────
bot = Bot(
    config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

dp.include_router(start.router)
dp.include_router(work.router)
dp.include_router(reports.router)
dp.include_router(settings.router)

async def send_weekly_reports():
    logger.info("Sending weekly reports...")
    for row in database.get_all_users():
        user_id = row["user_id"]
        try:
            await bot.send_message(user_id, report_builder.render_week_report(user_id))
        except Exception as e:
            logger.warning("Could not send weekly report to %s: %s", user_id, e)

async def main():
    database.init_db()
    scheduler.add_job(
        send_weekly_reports,
        "cron",
        day_of_week=config.WEEKLY_REPORT_DAY,
        hour=config.WEEKLY_REPORT_HOUR,
        minute=0,
    )
    scheduler.start()

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask healthcheck started")

    logger.info("Bot polling started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
