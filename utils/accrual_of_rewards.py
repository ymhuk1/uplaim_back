from sqlalchemy import select

from db import new_session
from models import Reward, Client, Transaction
from utils.notifications import notify


async def process_rewards():
    session = new_session()
    # Получаем все записи вознаграждений, у которых duration больше 0
    result = await session.execute(select(Reward).where(Reward.duration > 0))
    rewards = result.scalars().all()

    for reward in rewards:
        if reward.amount != 0:

            # Рассчитываем сумму для зачисления на баланс клиента
            amount_to_credit = round(reward.amount / reward.duration, 2)

            # Получаем клиента-агента
            agent = await session.get(Client, reward.agent_id)

            # Зачисляем сумму на баланс клиента
            new_transaction = Transaction(client=agent, balance=amount_to_credit, up_balance=0, transaction_type='deposit', status='success')
            session.add(new_transaction)

            # Уменьшаем duration на 1
            reward.duration -= 1

            # Уменьшаем amount на сумму, которую уже зачислили
            reward.amount -= amount_to_credit

            await notify(agent, 'balance', f"Зачислилось {amount_to_credit} рублей")

    # Обновляем записи в базе данных
    await session.commit()

