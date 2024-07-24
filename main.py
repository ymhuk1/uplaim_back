import asyncio
import os

import schedule
from fastapi import FastAPI, Request, Form, UploadFile, File, Depends
from fastapi.responses import FileResponse, HTMLResponse

from contextlib import asynccontextmanager

from fastapi.security import OAuth2PasswordBearer
from sqladmin import Admin
from starlette.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from admin import CityAdmin, UserAdmin, ClientAdmin, CategoryAdmin, CompanyAdmin, NewsAdmin, TagAdmin, ReviewAdmin, \
    BallsAdmin, CouponAdmin, TariffAdmin, SubscribedTariffAdmin, NotificationAdmin, ReferralAdmin, RewardAdmin, \
    ExchangeAdmin, TransactionAdmin, CompetitionAdmin, PrizeAdmin, TicketAdmin, TaskAdmin, TransactionCompetitionAdmin, \
    StoryAdmin, AdminAuth, SettingAdmin, QuestionAdmin, PushAdmin
from db import engine, new_session
from models import RevocationOfPrivacy, Company
from router.auth import auth_router as auth_router
from router.category import category_router
from router.company import company_router as company_router
from router.client import client_router
from router.competition import competition_router
from router.exchange import exchange_router
from router.notification import notify_router
from router.redirect_referral import redirect_router
from router.referral import referral_router
from router.story import story_router
from router.tariff import tariff_router
import sentry_sdk

from utils.sheduler import run_scheduler, stop_scheduler

sentry_sdk.init(
    dsn="https://ebde623893c3776c1f43e16d99d978f5@o1016854.ingest.us.sentry.io/4507310160740352",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

basedir = os.path.abspath(os.path.dirname(__file__))

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(auth_router)
app.include_router(company_router)
app.include_router(client_router)
app.include_router(story_router)
app.include_router(category_router)
app.include_router(tariff_router)
app.include_router(exchange_router)
app.include_router(referral_router)
app.include_router(notify_router)
app.include_router(competition_router)
app.include_router(redirect_router)

templates = Jinja2Templates(directory="templates")


@app.get("/robots.txt", include_in_schema=False)
async def robots_txt():
    return FileResponse("robots.txt")


@app.get("/acceptance", include_in_schema=False)
async def robots_txt():
    return FileResponse("static/acceptance.pdf")


@app.get("/agreement", include_in_schema=False)
async def robots_txt():
    return FileResponse("static/agreement.pdf")


@app.get("/privacy", include_in_schema=False)
async def robots_txt():
    return FileResponse("privacy.html")


@app.get("/", include_in_schema=False)
async def read_root():
    return FileResponse("uplaim.html")


@app.get("/revocation_of_privacy", response_class=HTMLResponse, include_in_schema=False)
async def revocation_of_privacy_form(request: Request):
    return templates.TemplateResponse("revocation_of_privacy.html", {"request": request})


@app.post("/revocation_of_privacy", include_in_schema=False)
async def revocation_of_privacy(request: Request, phone: str = Form(...), comment: str = Form(...)):
    feedback = RevocationOfPrivacy(phone=phone, comment=comment)
    # Здесь можно добавить логику для обработки отзыва, например, сохранение в базу данных
    return templates.TemplateResponse("success.html", {"request": request, "feedback": feedback})

app.mount("/static", StaticFiles(directory="static"), name="static")


authentication_backend = AdminAuth(secret_key="secret_key")
admin = Admin(app, engine, title='Uplaim', debug=True, authentication_backend=authentication_backend)

admin.add_view(CityAdmin)
admin.add_view(ClientAdmin)
admin.add_view(CategoryAdmin)
admin.add_view(CompanyAdmin)
admin.add_view(UserAdmin)
admin.add_view(NewsAdmin)
admin.add_view(TagAdmin)
admin.add_view(ReviewAdmin)
admin.add_view(BallsAdmin)
admin.add_view(CouponAdmin)
admin.add_view(TariffAdmin)
admin.add_view(SubscribedTariffAdmin)
admin.add_view(NotificationAdmin)
admin.add_view(ReferralAdmin)
admin.add_view(RewardAdmin)
admin.add_view(ExchangeAdmin)
admin.add_view(TransactionAdmin)
admin.add_view(CompetitionAdmin)
admin.add_view(PrizeAdmin)
admin.add_view(TicketAdmin)
admin.add_view(TaskAdmin)
admin.add_view(TransactionCompetitionAdmin)
admin.add_view(StoryAdmin)
admin.add_view(SettingAdmin)
admin.add_view(QuestionAdmin)
admin.add_view(PushAdmin)


@app.on_event("startup")
async def startup_event():
    global scheduler_task
    scheduler_task = asyncio.create_task(run_scheduler())


@app.on_event("shutdown")
async def shutdown_event():
    global scheduler_task
    stop_scheduler()
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        print("Scheduler task cancelled on shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
