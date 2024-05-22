from fastapi import APIRouter, Depends, HTTPException

from models import Category
from repository import CategoryRepository
from schemas import CategoryCompanies, CompanyModel

category_router = APIRouter(
    prefix="/api",
    tags=["Категория"]
)


@category_router.get('/categories')
async def get_categories():
    categories = await CategoryRepository.get_all_categories()

    if not categories:
        raise HTTPException(status_code=404, detail="No category found")
    return categories


@category_router.get('/company_categories', response_model=list[CompanyModel])
async def get_company_categories(category_id: CategoryCompanies = Depends()):
    company_categories = await CategoryRepository.get_company_categories(category_id)

    if not company_categories:
        raise HTTPException(status_code=404, detail="No category found")
    return company_categories
