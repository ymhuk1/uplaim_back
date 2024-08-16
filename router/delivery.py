from fastapi import APIRouter, Depends, HTTPException, Header, Query

from repository import DeliveryRepository
from schemas import CompanyModel, DeliveryCompanies, FavoritesInDelivery, DeliveryCompany, AddProductInBasket, \
    AddAddress

delivery_router = APIRouter(
    prefix="/api",
    tags=["Доставка"],
)


@delivery_router.get('/delivery_categories')
async def delivery_categories():
    delivery_categories = await DeliveryRepository.get_delivery_categories()

    if not delivery_categories:
        raise HTTPException(status_code=404, detail="Нет категорий с доставкой")
    return delivery_categories


@delivery_router.get('/delivery_companies', response_model=list[CompanyModel])
async def get_company_categories(data: DeliveryCompanies = Depends()):
    delivery_companies = await DeliveryRepository.get_delivery_companies(data)

    if not delivery_companies:
        raise HTTPException(status_code=404, detail="Нет компаний с доставкой")
    return delivery_companies


@delivery_router.post('/add_favorite')
async def add_favorite(data: FavoritesInDelivery):
    favorite = await DeliveryRepository.add_favorite(data)

    if not favorite:
        raise HTTPException(status_code=404, detail="Товар или компания не найдены!")
    return favorite


@delivery_router.get('/delivery_company')
async def get_company_categories(data: DeliveryCompany = Depends()):
    delivery_company = await DeliveryRepository.get_delivery_company(data)

    if not delivery_company:
        raise HTTPException(status_code=404, detail="Нет такой компании")
    return delivery_company


@delivery_router.post('/add_product')
async def add_product(data: AddProductInBasket):
    success_add_product = await DeliveryRepository.add_product_in_basket(data)

    if not success_add_product:
        raise HTTPException(status_code=404, detail="Клиент, компания или продукт не найдены")
    return success_add_product


@delivery_router.get('/baskets')
async def add_product(client_id: int):
    baskets = await DeliveryRepository.get_baskets(client_id)

    if not baskets:
        raise HTTPException(status_code=404, detail="Корзины не найдены")
    return baskets


@delivery_router.post('/add_address')
async def add_address(data: AddAddress):
    address = await DeliveryRepository.add_address(data)

    if not address:
        raise HTTPException(status_code=404, detail="Неправильный адрес")
    return address
