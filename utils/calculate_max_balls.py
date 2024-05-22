from models import Setting


def calculate_max_balls(tariff, company):
    settings = Setting.query.filter_by(id=1).first()
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
