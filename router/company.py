from typing import Optional, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from repository import CompanyRepository
from schemas import CompanyModel, ReviewCreateMessage, ReviewCreate, MessageSearchCompanies, \
    AssociateCompany

company_router = APIRouter(
    prefix="/api",
    tags=["Компания"],
)


@company_router.get("/companies", response_model=list[CompanyModel])
async def get_all_companies():
    companies = await CompanyRepository.get_all_companies()
    if not companies:
        raise HTTPException(status_code=404, detail="No companies found")
    return companies


@company_router.get("/companies/{company_id}", response_model=CompanyModel)
async def get_company(company_id: int, authorization: Optional[str] = Header(None)):
    company = await CompanyRepository.get_company(company_id, authorization)

    if not company:
        raise HTTPException(status_code=404, detail="No companies found")
    return company


@company_router.post("/associate_company")
async def associate_company(data: AssociateCompany, authorization: Optional[str] = Header(None)):
    result = await CompanyRepository.associate_company(data)

    if not result:
        raise HTTPException(status_code=404, detail="Client or company not found")
    return {"message": "Company associated with client"}


@company_router.post('/create_review', response_model=ReviewCreateMessage)
async def create_review(data: ReviewCreate, authorization: Optional[str] = Header(None)):
    result = await CompanyRepository.create_review(data)

    if not result:
        raise HTTPException(status_code=404, detail="not found")
    return result


@company_router.get("/company/search")
async def search_companies(term: Optional[str] = Query(None, alias="term")):
    if not term:
        return {"message": "No search term provided"}

    companies = await CompanyRepository.search_companies(term)
    if not companies:
        raise HTTPException(status_code=404, detail="No companies found matching the search term")

    return companies


@company_router.get("/coupon")
async def get_coupons():
    coupons = await CompanyRepository.get_coupons()
    if not coupons:
        raise HTTPException(status_code=404, detail="No coupons found")
    return coupons


@company_router.post("/add_coupon/{coupon_id}")
async def add_coupon(coupon_id: int, authorization: str = Header(alias="authorization")):
    coupon = await CompanyRepository.add_coupon(coupon_id, authorization)

    if not coupon:
        raise HTTPException(status_code=404, detail="No coupons found")
    return coupon
