from apscheduler.schedulers.asyncio import AsyncIOScheduler
from stats_logic import get_today, save_today

def schedule_jobs():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        lambda: save_today(get_today()),
        "cron",
        hour=0,
        minute=0
    )
    scheduler.start()
