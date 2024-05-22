
from fastapi import APIRouter, Depends, HTTPException, Header, Query

from repository import ReferralRepository

referral_router = APIRouter(
    prefix="/api",
    tags=["Рефералы"],
)


@referral_router.get("/referral")
async def list_referral(client_id: int = Query()):
    referral = await ReferralRepository.list_referral(client_id)
    if not referral:
        raise HTTPException(status_code=404, detail="No referral found")
    return referral


@referral_router.get("/my_reward")
async def my_reward(client_id: int = Query()):
    reward = await ReferralRepository.my_reward(client_id)
    if not reward:
        raise HTTPException(status_code=404, detail="No reward found")
    return reward
