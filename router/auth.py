from typing import Dict, Set
from fastapi import APIRouter, Depends, HTTPException, status
from repository import ClientRepository
from schemas import SendPhoneNumberIn, SendPhoneNumberOut, VerifySMSDataIn, VerifySMSDataOut, PasswordData, SPasswordData, LoginData, \
    SLoginData

auth_router = APIRouter(
    prefix="/api",
    tags=["Регистрация / Авторизация"],
)


@auth_router.post("/send_phone_number", response_model=SendPhoneNumberOut)
async def send_phone_number(client: SendPhoneNumberIn) -> SendPhoneNumberOut:
    data = await ClientRepository.send_phone_number(client)
    return data


@auth_router.post("/verify-sms-code")
async def verify_sms_code(data: VerifySMSDataIn) -> VerifySMSDataOut:
    is_valid = await ClientRepository.verify_sms_code(data)
    if is_valid:
        return {"message": "SMS code verified"}
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid SMS code")


@auth_router.post("/create-password")
async def create_password(data: PasswordData) -> SPasswordData:
    success = await ClientRepository.create_password(data)
    if success:
        return {"message": "Password created"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")


@auth_router.post("/login")
async def login(data: LoginData) -> SLoginData:
    is_authenticated = await ClientRepository.login(data)
    if is_authenticated:
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login credentials")
