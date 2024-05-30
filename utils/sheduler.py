import asyncio

import aioschedule as schedule

from db import new_session
from utils.accrual_of_rewards import process_rewards
from utils.competition import end_of_competition


async def job():
    await process_rewards()
    await end_of_competition()


# schedule.every(10).seconds.do(job)
schedule.every().day.at("00:00").do(job)


async def run_scheduler():
    try:
        while True:
            await schedule.run_pending()
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Scheduler has been cancelled {e}.")


def stop_scheduler():
    global running
    running = False

