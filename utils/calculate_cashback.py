from sqlalchemy import select

from models import Setting


async def calculate_cashback(tariff, company, session):
    result = await session.execute(select(Setting).where(Setting.id == 1))
    if result:
        settings = result.scalars().first()
        if settings is None:
            return None
    else:
        return None

    if company.cashback_company:
        cashback = int(company.cashback_company)
    else:
        cashback = 0

    cashback_tariffs = {
        'Free': int(
            cashback // settings.cashback_coefficient // settings.cashback_coefficient // settings.cashback_coefficient),
        'Pro': int(cashback // settings.cashback_coefficient // settings.cashback_coefficient),
        'Premium': int(cashback // settings.cashback_coefficient),
        'Vip': cashback
    }

    return cashback_tariffs
