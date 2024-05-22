
from fastapi import APIRouter, Depends, HTTPException, Header, Query

from repository import NotificationsRepository
from schemas import NotifyData

notify_router = APIRouter(
    prefix="/api",
    tags=["Уведомления"],
)


@notify_router.get("/notifications")
async def notifications(data: NotifyData = Depends()):
    result = await NotificationsRepository.get_notifications(data)
    if not result:
        raise HTTPException(status_code=404, detail="No referral found")
    return result
