from sqlalchemy import select, update

from models import Task, Transaction, client_tasks, TransactionCompetition
from utils.notifications import notify


async def check_tasks(session, task_type, company=None, client=None, referral=None, exchange=None, tariff=None):
    if task_type == "join":
        result = await session.execute(select(Task).where(Task.type == task_type, Task.company == company))
        tasks = result.scalars().all()
        if client:
            for task in tasks:
                if task:
                    client_task_association = client_tasks.insert().values(
                        task_id=task.id,
                        client_id=client.id,
                        quantity=task.quantity,
                        done='1'
                    )
                    await session.execute(client_task_association)
                    new_transaction = Transaction(client=client, balance=task.reward if task.reward_type == "rub" else 0, up_balance=task.reward if task.reward_type == "up" else 0,
                                                  transaction_type='deposit', status='success')
                    session.add(new_transaction)
                    new_transaction_competition = TransactionCompetition(name=task.name, task=task, client=client)
                    session.add(new_transaction_competition)

                    await notify(client, 'tasks', "Присоединение", f'Вы присоединились к компании {company} и получаете вознаграждение {task.reward} {task.reward_type}')
    elif task_type == "buy":
        pass
    elif task_type == "invite":
        result = await session.execute(select(Task).where(Task.type == task_type, Task.company == company))
        tasks = result.scalars().all()
        if client:
            for task in tasks:
                if task:
                    # Запрос на выборку записи в таблице client_tasks для текущего клиента и задачи
                    result = await session.execute(select(client_tasks).where(client_tasks.c.client_id == client.id,
                                                                              client_tasks.c.task_id == task.id))
                    client_task = result.first()

                    if client_task:
                        if int(client_task.quantity) <= int(task.quantity):
                            # Если запись существует, увеличиваем количество на 1
                            new_quantity = int(client_task.quantity) + 1
                            await session.execute(
                                update(client_tasks).
                                where(client_tasks.c.client_id == client.id, client_tasks.c.task_id == task.id).
                                values(quantity=str(new_quantity))
                            )

                            # Если количество равно требуемому, отправляем уведомление и создаем транзакцию
                            if new_quantity == int(task.quantity):
                                await notify(client, 'tasks',
                                             f'Вы выполнили задания и пригласили {task.quantity} друзей')

                                new_transaction = Transaction(
                                    client=client,
                                    balance=float(task.reward) if task.reward_type == "rub" else 0,
                                    up_balance=float(task.reward) if task.reward_type == "up" else 0,
                                    transaction_type='deposit',
                                    status='success'
                                )
                                session.add(new_transaction)
                                new_transaction_competition = TransactionCompetition(name=task.name, task=task,
                                                                                     client=client)
                                session.add(new_transaction_competition)
                    else:
                        # Если записи нет, создаем новую запись с quantity = 1
                        client_task_association = client_tasks.insert().values(
                            task_id=task.id,
                            client_id=client.id,
                            quantity='1',
                            done=task.quantity
                        )
                        await session.execute(client_task_association)
        await session.commit()

    elif task_type == "login":
        result = await session.execute(select(Task).where(Task.type == task_type, Task.company == company))
        tasks = result.scalars().all()
        if client:
            for task in tasks:
                if task:
                    # Запрос на выборку записи в таблице client_tasks для текущего клиента и задачи
                    result = await session.execute(select(client_tasks).where(client_tasks.c.client_id == client.id,
                                                                              client_tasks.c.task_id == task.id))
                    client_task = result.first()

                    if client_task:
                        if int(client_task.quantity) <= int(task.quantity):
                            # Если запись существует, увеличиваем количество на 1
                            new_quantity = int(client_task.quantity) + 1
                            await session.execute(
                                update(client_tasks).
                                where(client_tasks.c.client_id == client.id, client_tasks.c.task_id == task.id).
                                values(quantity=str(new_quantity))
                            )

                            # Если количество равно требуемому, отправляем уведомление и создаем транзакцию
                            if new_quantity == int(task.quantity):
                                await notify(client, 'tasks',
                                             f'Вы выполнили задания и зашли в приложение {task.quantity} раз', session)

                                new_transaction = Transaction(
                                    client=client,
                                    balance=float(task.reward) if task.reward_type == "rub" else 0,
                                    up_balance=float(task.reward) if task.reward_type == "up" else 0,
                                    transaction_type='deposit',
                                    status='success'
                                )
                                session.add(new_transaction)
                                new_transaction_competition = TransactionCompetition(name=task.name, task=task, client=client)
                                session.add(new_transaction_competition)
                    else:
                        # Если записи нет, создаем новую запись с quantity = 1
                        client_task_association = client_tasks.insert().values(
                            task_id=task.id,
                            client_id=client.id,
                            quantity='1',
                            done=task.quantity
                        )
                        await session.execute(client_task_association)
        await session.commit()

    elif task_type == "exchange":
        result = await session.execute(select(Task).where(Task.type == task_type, Task.company == company))
        tasks = result.scalars().all()
        if client:
            for task in tasks:
                if task:
                    # Запрос на выборку записи в таблице client_tasks для текущего клиента и задачи
                    result = await session.execute(select(client_tasks).where(client_tasks.c.client_id == client.id,
                                                                              client_tasks.c.task_id == task.id))
                    client_task = result.first()

                    if not client_task:
                        client_task_association = client_tasks.insert().values(
                            task_id=task.id,
                            client_id=client.id,
                            quantity='1',
                            done=task.quantity
                        )
                        await session.execute(client_task_association)
                        new_transaction = Transaction(
                            client=client,
                            balance=float(task.reward) if task.reward_type == "rub" else 0.0,
                            up_balance=float(task.reward) if task.reward_type == "up" else 0.0,
                            transaction_type='deposit',
                            status='success'
                        )
                        session.add(new_transaction)
                        new_transaction_competition = TransactionCompetition(name=task.name, task=task, client=client)
                        session.add(new_transaction_competition)
                        await notify(client, 'tasks', f'Вы выполнили задание и совершили сделку')

    elif task_type == "tariff" and tariff and client:
        # Запрос на выборку всех задач типа "tariff" для указанной компании
        result = await session.execute(select(Task).where(Task.type == task_type))
        tasks = result.scalars().all()

        for task in tasks:
            if task:
                result = await session.execute(select(client_tasks).where(client_tasks.c.client_id == client.id,
                                                                          client_tasks.c.task_id == task.id))
                client_task = result.first()

                if not client_task:
                    client_task_association = client_tasks.insert().values(
                        task_id=task.id,
                        client_id=client.id,
                        quantity='1',
                        done=task.quantity
                    )
                    await session.execute(client_task_association)
                    new_transaction = Transaction(
                        client=client,
                        balance=float(task.reward) if task.reward_type == "rub" else 0.0,
                        up_balance=float(task.reward) if task.reward_type == "up" else 0.0,
                        transaction_type='deposit',
                        status='success'
                    )
                    session.add(new_transaction)
                    new_transaction_competition = TransactionCompetition(name=task.name, task=task, client=client)
                    session.add(new_transaction_competition)
                    await notify(client, 'tasks', f'Вы выполнили задание и приобрели тариф')

        await session.commit()



# type = join, buy, invite, login, exchange, tariff,
# 1. Присоединиться к 1 определенной компании --------------
# 2. Присоединиться к 3, 5 определенным компаниям
# 3. Сделать покупку у определенной компании
# 4. Сделать покупки в какой-либо категории на заданную сумму
# 5. Сделать покупку в определенной компании на сумму не менее заданной
# 6. Совершить заданное количество покупок за определенный срок в заданной компании (или категории)
# 7.  Ежедневный вход в приложении в течении заданного количества дней -----
# 8. Пригласить заданное количество друзей в приложение
# 9. Совершить одну сделку на Бирже скидок -----
# 10. Подключить любой из платных тарифов -----

