import random
from datetime import datetime

from sqlalchemy import select, func

from db import new_session
from models import Competition, Ticket, Client
from utils.notifications import notify


async def end_of_competition():
    session = new_session()
    result = await session.execute(select(Competition).where(Competition.date_end == datetime.today().date()))
    competition = result.scalars().first()

    result = await session.execute(select(Ticket).where(Ticket.competition == competition, Ticket.client != None))
    tickets = result.scalars().all()
    active_tickets = [ticket for ticket in tickets if ticket.activate]
    no_active_tickets = [ticket for ticket in tickets if (ticket.activate is False or ticket.activate is None)]

    name_tickets_list = []
    for ticket in active_tickets:
        name_tickets_list.append(ticket.name)

    if name_tickets_list:
        winner_ticket = random.choice(name_tickets_list)

        winner = await session.execute(
            select(Client).join(Ticket).where(Ticket.name == winner_ticket)
        )
        winner_client = winner.scalars().first()

        prize_competition = competition.prizes[0]

        prize_competition.client = winner_client

        await notify(winner_client, 'competition', f"Вы выиграли конкурс «{competition.name}» и получаете приз «{prize_competition}», с вами скоро свяжутся")
        color = None
        for ticket in no_active_tickets:
            ticket.competition = None
            color = ticket.color

        new_competition = await session.execute(select(Competition.color is color))

        if new_competition:
            competition.ticket = no_active_tickets

    await session.commit()

# Поиск конкурса с date_end сегодня
# Выбор купленных билетов
# рандомно выбрать выигранный
# взять клиента из билета и добавить ему приз из конкурса
# отправить уведомление, что он выиграл конкурс и получил приз
# деактивировать участвовавшие билеты
# отвязать все билеты от конкурса которые не использовали
# найти свежий конкурс с таким же цветом и привязать билеты к нему
