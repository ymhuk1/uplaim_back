import asyncio

import aioschedule as schedule

from db import new_session
from utils.accrual_of_rewards import process_rewards


async def job(message='stuff'):
    await process_rewards()


# schedule.every(10).seconds.do(job)
schedule.every().day.at("19:21").do(job)


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

