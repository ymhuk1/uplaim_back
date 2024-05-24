import random
import string

import wtforms
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select, func
from starlette.requests import Request
from starlette.responses import RedirectResponse

from db import new_session
from models import User, City, Client, Category, Company, News, Tag, Review, Balls, Coupon, Tariff, SubscribedTariff, \
    Notification, Referral, Reward, Exchange, Transaction, Competition, Prize, Ticket, Task, TransactionCompetition, \
    Story, Setting
from utils.auth_user import get_password_hash, authenticate_user, create_access_token
from utils.save_photo import save_photo


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]
        user = await authenticate_user(email, password)
        if user:
            access_token = create_access_token({"sub": str(user.id)})
            request.session.update({"token": access_token})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> RedirectResponse | bool:
        token = request.session.get("token")

        if not token:
            return False
        return True


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.email, User.phone]
    column_details_exclude_list = [User.city_id]
    form_excluded_columns = [User.created_at, User.updated_at]
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"
    form_ajax_refs = {
        "city": {
            "fields": ("name", "id"),
            "order_by": City.id,
        }
    }

    async def on_model_change(self, form, model, is_created, request):
        password = form.get('password')
        if password:
            hashed_password = get_password_hash(password)
            form['password'] = hashed_password


class CityAdmin(ModelView, model=City):
    column_list = [City.id, City.name]
    form_excluded_columns = [User.created_at, User.updated_at]
    name = "Город"
    name_plural = "Города"
    icon = "fa-solid fa-city"


class ClientAdmin(ModelView, model=Client):
    column_list = [Client.id, Client.name, Client.phone, Client.tariff]
    form_excluded_columns = [Client.created_at, Client.updated_at, Client.reviews, Client.balls, Client.transactions, Client.notify, Client.referrals, Client.given_clients, Client.received_clients, Client.competitions, Client.tasks]
    name = "Клиент"
    name_plural = "Клиенты"
    icon = "fa-solid fa-users"
    form_ajax_refs = {
        "companies": {
            "fields": ("name", "id"),
            "order_by": Company.id,
        }
    }


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.name]
    form_excluded_columns = [Category.created_at, Category.updated_at, Category.exchange_categories]
    name = "Категория"
    name_plural = "Категории"
    icon = "fa-solid fa-align-left"
    # form_overrides = {
    #     'icon': wtforms.FileField
    # }

    # async def on_model_change(self, form, model, is_created, request):
    #     print('???????????/')
    #     filename = form.get('icon')
    #
    #     if filename:
    #         await save_photo(is_created, form, model, 'category', 'icon', )
    #     else:
    #         form['icon'] = None
    #
    # async def after_model_change(self, form, model, is_created, request):
    #     print('!!!!!!!!!')
    #
    # async def on_model_delete(self, model, request):
    #     print('11111111')
    #
    # async def after_model_delete(self, model, request):
    #     print('222222')


class CompanyAdmin(ModelView, model=Company):
    column_list = [Company.id, Company.name, Company.category, Company.news]
    form_excluded_columns = [Company.created_at, Company.updated_at, Company.news, Company.reviews, Company.balls, Company.coupons, Company.holder_company, Company.taker_company, Company.exchange_companies, Company.reviews_rating]
    column_details_exclude_list = [Company.category_id]
    name = "Компания"
    name_plural = "Компании"
    icon = "fa-solid fa-vcard"
    form_ajax_refs = {
        "clients": {
            "fields": ("name", "id"),
            "order_by": Client.id,
        }
    }
    form_overrides = {
                        'main_photo': wtforms.FileField,
                        'dop_photo_1': wtforms.FileField,
                        'dop_photo_2': wtforms.FileField,
                        'dop_photo_3': wtforms.FileField,
                        'dop_photo_4': wtforms.FileField,
                        'dop_photo_5': wtforms.FileField,
                      }

    async def on_model_change(self, form, model, is_created, request):
        if is_created is False:
            print('???????????/')

        filename = form.get('main_photo')
        dop_filename_1 = form.get('dop_photo_1')
        dop_filename_2 = form.get('dop_photo_2')
        dop_filename_3 = form.get('dop_photo_3')
        dop_filename_4 = form.get('dop_photo_4')
        dop_filename_5 = form.get('dop_photo_5')
        print('!!!!!!!!!!!')
        if filename:
            print('true')
            await save_photo(is_created, form, model, 'company', 'main_photo', 'main_photo')
        else:
            print('false')
            form['main_photo'] = None

        if dop_filename_1.filename:
            await save_photo(is_created, form, model, 'company', 'dop_photo_1', 'another_photo')
        else:
            form['dop_photo_1'] = None

        if dop_filename_2.filename:
            await save_photo(is_created, form, model, 'company', 'dop_photo_2', 'another_photo')
        else:
            form['dop_photo_2'] = None

        if dop_filename_3.filename:
            await save_photo(is_created, form, model, 'company', 'dop_photo_3', 'another_photo')
        else:
            form['dop_photo_3'] = None

        if dop_filename_4.filename:
            await save_photo(is_created, form, model, 'company', 'dop_photo_4', 'another_photo')
        else:
            form['dop_photo_4'] = None

        if dop_filename_5.filename:
            await save_photo(is_created, form, model, 'company', 'dop_photo_5', 'another_photo')
        else:
            form['dop_photo_5'] = None


class NewsAdmin(ModelView, model=News):
    column_list = [News.id, News.name, News.company]
    form_excluded_columns = [News.created_at, News.updated_at]
    name = "Новость"
    name_plural = "Новости"
    icon = "fa-solid fa-newspaper"
    form_overrides = {
        'photo': wtforms.FileField
    }

    async def on_model_change(self, form, model, is_created, request):
        filename = form.get('photo')

        if filename.filename:
            await save_photo(is_created, form, model, 'news', 'photo', )
        else:
            form['photo'] = None


class TagAdmin(ModelView, model=Tag):
    column_list = [Tag.id, Tag.name, Tag.companies, Tag.news]
    form_excluded_columns = [Tag.created_at, Tag.updated_at, Tag.companies, Tag.news]
    name = "Тег"
    name_plural = "Теги"
    icon = "fa-solid fa-tags"


class ReviewAdmin(ModelView, model=Review):
    column_list = [Review.id, Review.company, Review.rating]
    form_excluded_columns = [Review.created_at, Review.updated_at]
    name = "Отзыв"
    name_plural = "Отзывы"
    icon = "fa-solid fa-commenting"


class BallsAdmin(ModelView, model=Balls):
    column_list = [Balls.id, Balls.client, Balls.company, Balls.ball, Balls.hide_ball]
    form_excluded_columns = [Balls.created_at, Balls.updated_at]
    name = "Балл"
    name_plural = "Баллы"
    icon = "fa-solid fa-refresh"


class CouponAdmin(ModelView, model=Coupon):
    column_list = [Coupon.id, Coupon.name, Coupon.company]
    form_excluded_columns = [Coupon.created_at, Coupon.updated_at]
    name = "Купон"
    name_plural = "Купоны"
    icon = "fa-solid fa-ticket"


class TariffAdmin(ModelView, model=Tariff):
    column_list = [Tariff.id, Tariff.name, Tariff.for_client, Tariff.for_company]
    form_excluded_columns = [Tariff.created_at, Tariff.updated_at, Tariff.companies, Tariff.subscribed]

    name = "Тариф"
    name_plural = "Тарифы"
    icon = "fa-solid fa-flask"
    form_overrides = {
        'icon': wtforms.FileField
    }

    async def on_model_change(self, form, model, is_created, request):
        filename = form.get('icon')

        if filename.filename:
            await save_photo(is_created, form, model, 'tariff', 'icon', )
        else:
            form['icon'] = None


class SubscribedTariffAdmin(ModelView, model=SubscribedTariff):
    column_list = [SubscribedTariff.id, SubscribedTariff.tariff, SubscribedTariff.price, SubscribedTariff.duration]
    form_excluded_columns = [SubscribedTariff.created_at, SubscribedTariff.updated_at]

    name = "Подписка"
    name_plural = "Подписки"
    icon = "fa-solid fa-handshake"


class NotificationAdmin(ModelView, model=Notification):
    column_list = [Notification.id, Notification.title, Notification.client, Notification.type, Notification.read]
    form_excluded_columns = [Notification.created_at, Notification.updated_at]
    name = "Уведомление"
    name_plural = "Уведомления"
    icon = "fa-solid fa-bell"


class ReferralAdmin(ModelView, model=Referral):
    column_list = [Referral.id, Referral.referrer, Referral.referred, Referral.level]
    form_excluded_columns = [Referral.created_at, Referral.updated_at]
    name = "Реферал"
    name_plural = "Рефералы"
    icon = "fa-solid fa-user-plus"


class RewardAdmin(ModelView, model=Reward):
    column_list = [Reward.id, Reward.client, Reward.agent, Reward.tariff, Reward.duration, Reward.amount]
    form_excluded_columns = [Reward.created_at, Reward.updated_at]
    name = "Вознаграждение"
    name_plural = "Вознаграждения"
    icon = "fa-solid fa-diamond"


class ExchangeAdmin(ModelView, model=Exchange):
    column_list = [Exchange.id, Exchange.holder, Exchange.type_deal, Exchange.taker, Exchange.status]
    form_excluded_columns = [Exchange.created_at, Exchange.updated_at]
    name = "Сделка"
    name_plural = "Сделки"
    icon = "fa-solid fa-exchange"


class TransactionAdmin(ModelView, model=Transaction):
    column_list = [Transaction.id, Transaction.balance, Transaction.up_balance, Transaction.client, Transaction.transaction_type, Transaction.status]
    form_excluded_columns = [Transaction.created_at, Transaction.updated_at]
    name = "Транзакция"
    name_plural = "Транзакции"
    icon = "fa-solid fa-random"


class CompetitionAdmin(ModelView, model=Competition):
    column_list = [Competition.id, Competition.name, Competition.prizes, Competition.quantity_ticket, Competition.date_end]
    form_excluded_columns = [Competition.created_at, Competition.updated_at, Competition.clients, Competition.prizes, Competition.tickets]

    name = "Конкурс"
    name_plural = "Конкурсы"
    icon = "fa-solid fa-cubes"
    form_overrides = {
        'photo': wtforms.FileField
    }

    async def on_model_change(self, form, model, is_created, request):
        filename = form.get('photo')

        if filename.filename:
            await save_photo(is_created, form, model, 'competition', 'photo', )
        else:
            form['photo'] = None

    async def after_model_change(self, data, model, is_created, request):
        if is_created:
            if model.quantity_ticket > 0:
                async with new_session() as session:
                    existing_tickets_count = await session.execute(
                        select(func.count(Ticket.id)).where(Ticket.competition_id == model.id)
                    )
                    existing_tickets_count = existing_tickets_count.scalar()

                    tickets_to_create = model.quantity_ticket - existing_tickets_count

                    if tickets_to_create > 0:
                        tickets = []
                        for _ in range(tickets_to_create):
                            ticket_name = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                            ticket = Ticket(
                                name=ticket_name,
                                color=model.color,
                                competition_id=model.id
                            )
                            tickets.append(ticket)

                        session.add_all(tickets)
                        await session.commit()


class PrizeAdmin(ModelView, model=Prize):
    column_list = [Prize.id, Prize.name, Prize.competition, Prize.client]
    form_excluded_columns = [Prize.created_at, Prize.updated_at]

    name = "Приз"
    name_plural = "Призы"
    icon = "fa-solid fa-gift"
    form_overrides = {
        'photo': wtforms.FileField
    }

    async def on_model_change(self, form, model, is_created, request):
        filename = form.get('photo')

        if filename.filename:
            await save_photo(is_created, form, model, 'prize', 'photo', )
        else:
            form['photo'] = None


class TicketAdmin(ModelView, model=Ticket):
    column_list = [Ticket.id, Ticket.name, Ticket.client, Ticket.competition, Ticket.activate]
    form_excluded_columns = [Ticket.created_at, Ticket.updated_at]

    name = "Билет"
    name_plural = "Билеты"
    icon = "fa-solid fa-credit-card"


class TaskAdmin(ModelView, model=Task):
    column_list = [Task.id, Task.name, Task.date_end]
    form_excluded_columns = [Ticket.created_at, Ticket.updated_at, Task.clients]

    name = "Задание"
    name_plural = "Задания"
    icon = "fa-solid fa-tasks"
    form_overrides = {
        'photo': wtforms.FileField
    }

    async def on_model_change(self, form, model, is_created, request):
        filename = form.get('photo')

        if filename.filename:
            await save_photo(is_created, form, model, 'task', 'photo', )
        else:
            form['photo'] = None


class TransactionCompetitionAdmin(ModelView, model=TransactionCompetition):
    column_list = [TransactionCompetition.id]
    form_excluded_columns = [TransactionCompetition.created_at, TransactionCompetition.updated_at]

    name = "Транзакция конкурса"
    name_plural = "Транзакции конкурса"
    icon = "fa-solid fa-history"


class StoryAdmin(ModelView, model=Story):
    column_list = [Story.id, Story.name, Story.visible, Story.show_in_search]
    form_excluded_columns = [Story.created_at, Story.updated_at]

    name = "Истории"
    name_plural = "Истории"
    icon = "fa-solid fa-archive"

    form_overrides = {
        'icon': wtforms.FileField,
        'photo': wtforms.FileField
    }

    async def on_model_change(self, form, model, is_created, request):
        filename = form.get('icon')
        photo_filename = form.get('photo')

        if filename.filename:
            await save_photo(is_created, form, model, 'story', 'icon', )
        else:
            form['icon'] = None

        if photo_filename.filename:
            await save_photo(is_created, form, model, 'story', 'photo', )
        else:
            form['photo'] = None


class SettingAdmin(ModelView, model=Setting):
    column_list = [Setting.id]
    form_excluded_columns = [Story.created_at, Story.updated_at]
    name = "Настройки"
    name_plural = "Настройки"
    icon = "fa-solid fa-archive"
