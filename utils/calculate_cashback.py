from models import Setting


def calculate_cashback(tariff, company):
    settings = Setting.query.filter_by(id=1).first()
    if company.cashback:
        cashback = int(company.cashback)
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
