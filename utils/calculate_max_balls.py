from sqlalchemy import select

from models import Setting


async def calculate_max_balls(tariff, company, session):
    settings = await session.execute(select(Setting).where(Setting.id == 1))
    if company.max_pay_point:
        max_pay_point = int(company.max_pay_point)
    else:
        max_pay_point = 0

    max_pay_point_tariffs = {
        'Free': int(
            max_pay_point // settings.balls_deduction_coefficient // settings.balls_deduction_coefficient // settings.balls_deduction_coefficient),
        'Pro': int(max_pay_point // settings.balls_deduction_coefficient // settings.balls_deduction_coefficient),
        'Premium': int(max_pay_point // settings.balls_deduction_coefficient),
        'Vip': int(max_pay_point)
    }

    return max_pay_point_tariffs
