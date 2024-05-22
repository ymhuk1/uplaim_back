from fastapi import APIRouter, Depends, HTTPException

from repository import TariffRepository
from schemas import GetSubscribedTariffs, AssociateTariff

tariff_router = APIRouter(
    prefix="/api",
    tags=["Тариф"],
)


@tariff_router.get('/tariffs')
async def get_all_tariffs():
    tariffs = await TariffRepository.get_all_tariffs()

    if not tariffs:
        raise HTTPException(status_code=404, detail="No tariffs found")
    return tariffs


@tariff_router.get('/subscriptions')
async def get_subscriptions(data: GetSubscribedTariffs = Depends()):
    subscriptions = await TariffRepository.get_subscriptions(data)

    if not subscriptions:
        raise HTTPException(status_code=404, detail="No subscriptions found")
    return subscriptions


@tariff_router.post('/associate_tariff')
async def associate_tariff(data: AssociateTariff):
    result = await TariffRepository.associate_tariff(data)

    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result
