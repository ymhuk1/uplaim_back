import random
from datetime import datetime
from sqlalchemy.future import select

from db import new_session
from models import Competition, Ticket, Client
from utils.notifications import notify


async def end_of_competition():
    session = new_session()
    today = datetime.today().date()

    competition = await get_ending_competition(session, today)
    if not competition:
        return

    active_tickets, no_active_tickets = await get_tickets_by_competition(session, competition)

    if active_tickets:
        winner_ticket_name = select_random_winner(active_tickets)
        winner_client = await get_winner_client(session, winner_ticket_name)

        if winner_client:
            await award_prize_to_winner(session, competition, winner_client)
            await notify_winner(winner_client, competition, session=session)

    await reassign_inactive_tickets(session, no_active_tickets)

    await session.commit()


async def get_ending_competition(session, today):
    result = await session.execute(
        select(Competition).where(Competition.date_end == today)
    )
    return result.scalars().first()


async def get_tickets_by_competition(session, competition):
    result = await session.execute(
        select(Ticket).where(Ticket.competition == competition, Ticket.client != None)
    )
    tickets = result.scalars().all()
    active_tickets = [ticket for ticket in tickets if ticket.activate]
    no_active_tickets = [ticket for ticket in tickets if not ticket.activate]
    return active_tickets, no_active_tickets


def select_random_winner(active_tickets):
    name_tickets_list = [ticket.name for ticket in active_tickets]
    return random.choice(name_tickets_list)


async def get_winner_client(session, winner_ticket_name):
    result = await session.execute(
        select(Client).join(Ticket).where(Ticket.name == winner_ticket_name)
    )
    return result.scalars().first()


async def award_prize_to_winner(session, competition, winner_client):
    prize_competition = competition.prizes[0]
    prize_competition.client = winner_client


async def notify_winner(winner_client, competition, session):
    await notify(
        winner_client, 'competition',
        f"Вы выиграли конкурс «{competition.name}» и получаете приз «{competition.prizes[0]}», с вами скоро свяжутся"
    )


async def reassign_inactive_tickets(session, no_active_tickets):
    if not no_active_tickets:
        return

    color = no_active_tickets[0].color
    result = await session.execute(
        select(Competition).where(Competition.color == color)
    )
    new_competition = result.scalars().first()

    if new_competition:
        for ticket in no_active_tickets:
            ticket.competition = new_competition
