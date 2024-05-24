from sqlalchemy import select

from db import new_session
from models import Client


async def get_balance(client_id):
    async with new_session() as session:
        result = await session.execute(select(Client).where(Client.id == client_id))
        client = result.scalars().first()

        transactions = client.transactions

        balance = 0
        for transaction in transactions:
            if transaction.status == "success":
                if transaction.transaction_type == "deposit":
                    balance += transaction.balance
                elif transaction.transaction_type == "withdraw":
                    balance -= transaction.balance

        return balance


async def get_up_balance(client_id):
    async with new_session() as session:
        result = await session.execute(select(Client).where(Client.id == client_id))
        client = result.scalars().first()

        transactions = [t for t in client.transactions if t.up_balance != None and t.status == "success"]

        up_balance = 0
        for transaction in transactions:
            if transaction.transaction_type == "deposit":
                up_balance += transaction.up_balance
            elif transaction.transaction_type == "withdraw":
                up_balance -= transaction.up_balance

        return up_balance
