from typing import Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Header, Body

from repository import ExchangeRepository
from schemas import ExchangeCreateIn, UpdateExchange

exchange_router = APIRouter(
    prefix="/api",
    tags=["Сделки"],
)


@exchange_router.get('/exchange/my_balls')
async def my_balls(category: Optional[str] = Query(None, alias="category"),
                   city: Optional[str] = Query(None, alias="city"), authorization: str = Header(alias="authorization")):
    result = await ExchangeRepository.my_balls(category, city, authorization)

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@exchange_router.get('/exchange/all_companies')
async def all_companies(city: Optional[str] = Query(None, alias="city"),
                        category: Optional[str] = Query(None, alias="category")):
    result = await ExchangeRepository.all_companies(city, category)

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@exchange_router.get('/exchange/all_cities')
async def all_cities():
    result = await ExchangeRepository.all_cities()

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@exchange_router.get('/exchange/all_categories')
async def all_categories():
    result = await ExchangeRepository.all_categories()

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@exchange_router.get('/exchange/active_exchange')
async def active_exchange(client_id: int = Query(None, alias="client_id"), available: Optional[bool] = Query(None, alias="available"), city: Optional[str] = Query(None, alias="city")):
    result = await ExchangeRepository.active_exchange(client_id, available, city)

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@exchange_router.get('/exchange/proposed_exchange/{taker_id}')
async def proposed_exchange(taker_id: int):
    result = await ExchangeRepository.proposed_exchange(taker_id)

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@exchange_router.post('/exchange/create')
async def create(data: ExchangeCreateIn):
    result = await ExchangeRepository.create(data)

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@exchange_router.patch('/exchange/update/{exchange_id}')
async def update_exchange(exchange_id, data: UpdateExchange):
    result = await ExchangeRepository.update_exchange(exchange_id, data)

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@exchange_router.patch('/exchange/accept/{exchange_id}/{taker_id}')
async def accept_exchange(exchange_id: int, taker_id: int, taker_company_id: int = Body(embed=True)):
    result = await ExchangeRepository.accept_exchange(exchange_id, taker_id, taker_company_id)

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@exchange_router.delete('/exchange/delete/{exchange_id}')
async def delete_exchange(exchange_id: int):
    result = await ExchangeRepository.delete_exchange(exchange_id)

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result

