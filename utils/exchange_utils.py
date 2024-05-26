from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Balls, Transaction
from db import new_session
from utils.transactions import get_balance, get_up_balance


async def has_enough_balls_in_company(client, company_id, required_balls):
    async with new_session() as session:
        result = await session.execute(select(Balls).where(Balls.client_id == client, Balls.company_id == company_id))
        client_balls_entry = result.scalars().first()
        if not client_balls_entry:
            return False
        elif required_balls is not None:
            return client_balls_entry.ball >= int(required_balls)
        return True


async def has_enough_saveup(client, get_saveup):
    up_balance = await get_up_balance(client)
    if not up_balance:
        return False
    if get_saveup is not None:
        return up_balance >= int(get_saveup)
    return True


async def has_enough_cash(client, get_cash):
    balance = await get_balance(client)
    if not balance:
        return False
    if get_cash is not None:
        return balance >= int(get_cash)
    return True


async def has_enough_balls(client_id, company_id, required_balls):
    async with new_session() as session:
        result = await session.execute(func.sum(Balls.ball)).filter_by(client_id=int(client_id), company_id=int(company_id)).scalar()
        total_balls = result.scalars().all()
        if total_balls is None:
            total_balls = 0

        return total_balls >= int(required_balls)


async def from_holder_in_taker_balls(holder, taker, existing_exchange):
    async with new_session() as session:
        taker_balls = next((ball for ball in taker.balls if ball.company_id == existing_exchange.holder_company_id), None)
        holder_balls = next((ball for ball in holder.balls if ball.company_id == existing_exchange.holder_company_id), None)

        if taker_balls is None:
            new_taker_balls = Balls(company_id=existing_exchange.holder_company_id, ball=0, hide_ball=0)
            taker.balls.append(new_taker_balls)
            taker_balls = new_taker_balls
            await session.commit()

        if holder_balls.ball > existing_exchange.give_balls:
            holder_balls.ball -= existing_exchange.give_balls
            taker_balls.ball += existing_exchange.give_balls
            await session.commit()
            return holder_balls, taker_balls, None
        else:
            return None, None, {"error": "У держателя не хватает баллов"}


async def from_taker_in_holder_balls(holder, taker, taker_company_id, existing_exchange):
    async with new_session() as session:
        taker_balls = next((ball for ball in taker.balls if ball.company_id == int(taker_company_id)), None)
        holder_balls = next((ball for ball in holder.balls if ball.company_id == int(taker_company_id)), None)

        if taker_balls is None:
            new_taker_balls = Balls(company_id=int(taker_company_id), ball=0, hide_ball=0)
            taker.balls.append(new_taker_balls)
            taker_balls = new_taker_balls
            await session.commit()

        if holder_balls is None:
            new_holder_balls = Balls(company_id=int(taker_company_id), ball=0, hide_ball=0)
            holder.balls.append(new_holder_balls)
            holder_balls = new_holder_balls
            await session.commit()

        if taker_balls.ball > existing_exchange.get_balls:
            taker_balls.ball -= existing_exchange.get_balls
            holder_balls.ball += existing_exchange.get_balls
            await session.commit()
            return holder_balls, taker_balls, None
        else:
            return None, None, {"error": "У вас не хватает баллов"}


async def from_holder_in_taker_cash_or_up(holder, taker, existing_exchange, session: AsyncSession):
    if existing_exchange.give_cash:
        balance = await get_balance(holder.id)
        # print('balance: ', balance)

        if balance > existing_exchange.give_cash:
            new_holder_transaction = Transaction(balance=existing_exchange.give_cash, transaction_type='withdraw',
                                                 status='success', client=holder)
            new_taker_transaction = Transaction(balance=existing_exchange.give_cash, transaction_type='deposit',
                                                status='success', client=taker)
            session.add(new_holder_transaction)
            session.add(new_taker_transaction)

            await session.commit()
            return None
        else:
            return {"error": "У держателя баллов не хватает денег"}

    elif existing_exchange.give_saveup:
        up_balance = await get_up_balance(holder.id)

        if up_balance > existing_exchange.give_saveup:
            new_holder_transaction = Transaction(up_balance=existing_exchange.give_saveup, transaction_type='withdraw',
                                                 status='success', client=holder)
            new_taker_transaction = Transaction(up_balance=existing_exchange.give_saveup, transaction_type='deposit',
                                                status='success', client=taker)

            session.add(new_holder_transaction)
            session.add(new_taker_transaction)

            await session.commit()
            return None
        else:
            return {"error": "У держателя баллов не хватает апов"}


async def from_taker_in_holder_cash_or_up(holder, taker, existing_exchange, session: AsyncSession):
    if existing_exchange.get_cash:
        if await get_balance(taker) > existing_exchange.get_cash:
            taker.balance[0].balance -= existing_exchange.get_cash
            holder.balance[0].balance += existing_exchange.get_cash
            await session.commit()
            return None
        else:
            return {"error": "У держателя баллов не хватает денег"}
    elif existing_exchange.get_saveup:
        if await get_up_balance(taker) > existing_exchange.get_saveup:
            taker.up_balance[0].up_balance -= existing_exchange.get_saveup
            holder.up_balance[0].up_balance += existing_exchange.get_saveup
            await session.commit()
            return None
        else:
            return {"error": "У держателя баллов не хватает апов"}

