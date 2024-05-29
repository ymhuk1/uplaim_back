from sqlalchemy import select

from db import new_session
from models import Reward, Client, Transaction
from utils.notifications import notify


async def process_rewards():
    async with new_session as session:
        async with session.begin():
            # Получаем все записи вознаграждений, у которых duration больше 0
            result = await session.execute(select(Reward).where(Reward.duration > 0))
            rewards = result.scalars().all()
            print(len(rewards))

            for reward in rewards:
                # Рассчитываем сумму для зачисления на баланс клиента
                amount_to_credit = reward.amount / reward.duration

                # Получаем клиента-агента
                agent = await session.get(Client, reward.agent_id)

                # Получаем его баланс
                # result = await session.execute(select(Balance).where(Balance.client_id == reward.agent_id))
                # agent_balance = result.scalars().first()

                # if agent and agent_balance:
                # Зачисляем сумму на баланс клиента
                new_transaction = Transaction(client=agent, balance=amount_to_credit, up_balance=0, transaction_type='deposit', status='success')
                session.add(new_transaction)
                # agent_balance.balance += amount_to_credit

                # Уменьшаем duration на 1
                reward.duration -= 1

                # Уменьшаем amount на сумму, которую уже зачислили
                reward.amount -= amount_to_credit

                await notify(agent, 'balance', f"Зачислилось {amount_to_credit} рублей")

                # Обновляем записи в базе данных
                await session.commit()
