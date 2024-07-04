from sqlalchemy import select

from models import Referral, Client
from utils.notifications import notify
from utils.tasks import check_tasks


async def process_referral(referral_code, new_client, session):
    result = await session.execute(select(Client).where(Client.referral_link == referral_code))
    referrer = result.scalars().first()

    if referrer:
        await notify(referrer, 'referral', 'Новый друг', 'Присоединился реферал вашего 1-го уровня')
        await check_tasks(session, 'invite', client=referrer)
        await create_referral_chain(referrer, new_client, levels=5, session=session)


async def create_referral_chain(referrer, referred, levels=5, session=None):
    for level in range(1, levels + 1):
        new_referral = Referral(referrer=referrer, referred=referred, level=str(level))

        session.add(new_referral)
        await session.commit()

        result = await session.execute(select(Client).join(Referral, Client.id == Referral.referrer_id).where(Referral.referred_id == referrer.id))
        referrer = result.scalars().first()

        if referrer:
            referrer = referrer
        else:
            break



