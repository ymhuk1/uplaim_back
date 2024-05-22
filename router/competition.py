
from fastapi import APIRouter, Depends, HTTPException, Query, Header, Body

from repository import CompetitionRepository

competition_router = APIRouter(
    prefix="/api",
    tags=["Конкурсы"],
)


@competition_router.get('/competitions')
async def competitions():
    result = await CompetitionRepository.all_competitions()

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@competition_router.get('/prizes')
async def prizes():
    result = await CompetitionRepository.all_prizes()

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@competition_router.get('/my_tickets')
async def my_tickets(client_id: int = Query(None, alias="client_id")):
    result = await CompetitionRepository.my_tickets(client_id)

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@competition_router.get('/tickets_on_sell')
async def tickets_on_sell():
    result = await CompetitionRepository.tickets_on_sell()

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@competition_router.post('/buy_tickets')
async def buy_tickets(client_id: int, competition_id: int, quantity: int):
    result = await CompetitionRepository.buy_tickets(client_id, competition_id, quantity)

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@competition_router.get('/all_tasks')
async def all_tasks():
    result = await CompetitionRepository.all_tasks()

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@competition_router.get('/all_transaction_tasks')
async def all_transaction_tasks():
    result = await CompetitionRepository.all_transaction_tasks()

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@competition_router.get('/all_questions')
async def all_questions():
    result = await CompetitionRepository.all_transaction_tasks()

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result

