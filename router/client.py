from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Query

from repository import ClientRepository, FranchiseRepository
from schemas import ClientIn, ClientOut, CompanyModel, ClientEditDataIn, FranchiseData

client_router = APIRouter(
    prefix="/api",
    tags=["Клиент"],
)


@client_router.get("/client")
async def get_client(authorization: str = Header(alias="authorization")):
    client = await ClientRepository.get_client(authorization)

    if not client:
        raise HTTPException(status_code=404, detail="No client found")
    return client


@client_router.get("/my_companies", response_model=list[CompanyModel])
async def get_client_companies(authorization: str = Header(alias="authorization")):
    my_companies = await ClientRepository.get_client_companies(authorization)

    if not my_companies:
        raise HTTPException(status_code=404, detail="No companies found")
    return my_companies


@client_router.post("/edit_client")
async def edit_client(data: ClientEditDataIn, authorization: str = Header(alias="authorization")):
    client = await ClientRepository.edit_client(data, authorization)

    if not client:
        raise HTTPException(status_code=404, detail="No client found")
    return client


@client_router.get("/get_coupons_categories")
async def get_coupons_categories(category_id: int, client_id: int):
    coupons = await ClientRepository.get_coupons_categories(category_id, client_id)

    if not coupons:
        raise HTTPException(status_code=404, detail="No coupons found")
    return coupons


@client_router.get("/transactions")
async def get_transactions(client_id: int, balls: Optional[bool] = Query(None, alias="balls"), cash: Optional[bool] = Query(None, alias="cash"), up: Optional[bool] = Query(None, alias="up")):
    transactions = await ClientRepository.get_transactions(client_id, balls, cash, up)

    if not transactions:
        raise HTTPException(status_code=401, detail="No transaction found")
    return transactions


@client_router.post("/create_request")
async def create_request(data: FranchiseData):
    result = await FranchiseRepository.create_request(data)

    if not result:
        raise HTTPException(status_code=404, detail="not found")
    return result
