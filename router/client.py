from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Header

from repository import ClientRepository
from schemas import ClientIn, ClientOut, CompanyModel, ClientEditDataIn

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
