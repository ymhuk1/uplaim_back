import random
import string

import wtforms
from fastapi import File
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select, func
from starlette.requests import Request
from starlette.responses import RedirectResponse

from db import new_session
from models import User, City, Client, Category, Company, News, Tag, Review, Balls, Coupon, Tariff, SubscribedTariff, \
    Notification, Referral, Reward, Exchange, Transaction, Competition, Prize, Ticket, Task, TransactionCompetition, \
    Story, Setting, Question, Push, Product, ProductsCategory, Favorite, Basket, Order, ClientAddress
from utils.auth_user import get_password_hash, authenticate_user, create_access_token


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
    form_overrides = {
        "type": wtforms.SelectField,
    }
    form_args = {
        "type": {
            "label": "Type",
            "choices": [('admin', 'Администратор'), ('franchise', 'Франшиза')]
        },
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
    form_excluded_columns = [Client.created_at, Client.updated_at, Client.reviews, Client.balls, Client.transactions,
                             Client.notify, Client.referrals, Client.given_clients, Client.received_clients,
                             Client.competitions, Client.tasks]
    name = "Клиент"
    name_plural = "Клиенты"
    icon = "fa-solid fa-users"
    form_ajax_refs = {
        "companies": {
            "fields": ("name", "id"),
            "order_by": Company.id,
        }
    }
    form_overrides = {
        "gender": wtforms.SelectField,
    }
    form_args = {
        "gender": {
            "label": "Gender",
            "choices": [('man', 'Мужчина'), ('woman', 'Женщина')]
        },
    }


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.name]
    form_excluded_columns = [Category.created_at, Category.updated_at, Category.exchange_categories]
    name = "Категория"
    name_plural = "Категории"
    icon = "fa-solid fa-align-left"
    form_overrides = {
        "color": wtforms.ColorField
    }


class CompanyAdmin(ModelView, model=Company):
    column_list = [Company.id, Company.name, Company.category, Company.news]
    form_excluded_columns = [Company.created_at, Company.updated_at, Company.news, Company.reviews, Company.balls,
                             Company.coupons, Company.holder_company, Company.taker_company, Company.exchange_companies,
                             Company.reviews_rating, Company.holder_company, Company.another_photo, Company.cashback,
                             Company.max_pay_point]
    column_details_exclude_list = [Company.category_id, Company.another_photo, Company.external_links, Company.cashback,
                                   Company.max_pay_point]
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
        "color": wtforms.ColorField,
    }

    async def on_model_change(self, form, model, is_created, request):
        if form['main_photo'].size is None:
            del form['main_photo']

        await super().on_model_change(form, model, is_created, request)


class NewsAdmin(ModelView, model=News):
    column_list = [News.id, News.name, News.company]
    form_excluded_columns = [News.created_at, News.updated_at]
    name = "Новость"
    name_plural = "Новости"
    icon = "fa-solid fa-newspaper"


class TagAdmin(ModelView, model=Tag):
    column_list = [Tag.id, Tag.name, Tag.companies, Tag.news]
    form_excluded_columns = [Tag.created_at, Tag.updated_at, Tag.companies, Tag.news]
    name = "Тег"
    name_plural = "Теги"
    icon = "fa-solid fa-tags"
    form_overrides = {
        "text_color": wtforms.ColorField,
        "background_color": wtforms.ColorField
    }


class ReviewAdmin(ModelView, model=Review):
    column_list = [Review.id, Review.company, Review.rating]
    form_excluded_columns = [Review.created_at, Review.updated_at]
    name = "Отзыв"
    name_plural = "Отзывы"
    icon = "fa-solid fa-commenting"
    form_overrides = {
        "rating": wtforms.SelectField,
    }
    form_args = {
        "rating": {
            "label": "Rating",
            "choices": [(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]
        },
    }


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
    form_overrides = {
        "color": wtforms.ColorField
    }


class TariffAdmin(ModelView, model=Tariff):
    column_list = [Tariff.id, Tariff.name, Tariff.for_client, Tariff.for_company]
    form_excluded_columns = [Tariff.created_at, Tariff.updated_at, Tariff.companies, Tariff.subscribed]
    name = "Тариф"
    name_plural = "Тарифы"
    icon = "fa-solid fa-flask"
    form_overrides = {
        "color": wtforms.ColorField
    }


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
    form_overrides = {
        "level": wtforms.SelectField,
    }
    form_args = {
        "level": {
            "label": "Level",
            "choices": [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]
        },
    }


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
    form_overrides = {
        "type_deal": wtforms.SelectField,
        "status": wtforms.SelectField,
    }
    form_args = {
        "type_deal": {
            "label": "Type deal",
            "choices": [('buy', 'Купить'), ('exchange', 'Обменять'), ('exchange_sell', 'Обменять/продать'),
                        ('sell', 'Продать')]
        },
        "status": {
            "label": "Status",
            "choices": [('active', 'Активная'), ('draft', 'Черновик'), ('completed', 'Выполненная'),
                        ('hide', 'Скрытая'), ('canceled', 'Отмененная')]
        },
    }


class TransactionAdmin(ModelView, model=Transaction):
    column_list = [Transaction.id, Transaction.balance, Transaction.up_balance, Transaction.client,
                   Transaction.transaction_type, Transaction.status]
    form_excluded_columns = [Transaction.created_at, Transaction.updated_at]
    name = "Транзакция"
    name_plural = "Транзакции"
    icon = "fa-solid fa-random"
    form_overrides = {
        "transaction_type": wtforms.SelectField,
        "status": wtforms.SelectField,
    }
    form_args = {
        "transaction_type": {
            "label": "Transaction type",
            "choices": [('deposit', 'Пополнение'), ('withdraw', 'Снятие')]
        },
        "status": {
            "label": "Status",
            "choices": [('success', 'Успешно'), ('fail', 'Ошибка'), ('hold', 'Заморожено')]
        },
    }


class CompetitionAdmin(ModelView, model=Competition):
    column_list = [Competition.id, Competition.name, Competition.prizes, Competition.quantity_ticket,
                   Competition.date_end]
    form_excluded_columns = [Competition.created_at, Competition.updated_at, Competition.clients, Competition.prizes,
                             Competition.tickets]
    name = "Конкурс"
    name_plural = "Конкурсы"
    icon = "fa-solid fa-cubes"
    form_overrides = {
        "color": wtforms.ColorField
    }

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


class TicketAdmin(ModelView, model=Ticket):
    column_list = [Ticket.id, Ticket.name, Ticket.client, Ticket.competition, Ticket.activate]
    form_excluded_columns = [Ticket.created_at, Ticket.updated_at]
    name = "Билет"
    name_plural = "Билеты"
    icon = "fa-solid fa-credit-card"
    form_overrides = {
        "color": wtforms.ColorField
    }


class TaskAdmin(ModelView, model=Task):
    column_list = [Task.id, Task.name, Task.date_end]
    form_excluded_columns = [Ticket.created_at, Ticket.updated_at, Task.clients]
    form_overrides = {
        "reward_type": wtforms.SelectField,
        "type": wtforms.SelectField,
        "status": wtforms.SelectField,

    }
    form_args = {
        "reward_type": {
            "label": "Reward Type",
            "choices": [('rub', 'Руб'), ('up', 'Up')]
        },
        "type": {
            "label": "Task Type",
            "choices": [('join', 'Присоединение'), ('buy', 'Покупка'), ('invite', 'Приглашение'), ('login', 'Вход'),
                        ('exchange', 'Сделка'), ('tariff', 'Тариф'), ]
        },
        "status": {
            "label": "Status",
            "choices": [('activate', 'Активная'), ('deactivate', 'Неактивная')]
        }
    }
    name = "Задание"
    name_plural = "Задания"
    icon = "fa-solid fa-tasks"


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


class QuestionAdmin(ModelView, model=Question):
    column_list = [Question.id, Question.place, Question.question, Question.answer]
    form_excluded_columns = [Question.created_at, Question.updated_at]

    name = "Вопрос"
    name_plural = "Вопросы"
    icon = "fa-solid fa-question-circle"


class SettingAdmin(ModelView, model=Setting):
    column_list = [Setting.id]
    form_excluded_columns = [Story.created_at, Story.updated_at]
    name = "Настройки"
    name_plural = "Настройки"
    icon = "fa-solid fa-sliders"


class PushAdmin(ModelView, model=Push):
    column_list = [Push.id]
    form_excluded_columns = [Push.created_at, Push.updated_at]
    name = "Пуш"
    name_plural = "Пуши"
    icon = "fa-solid fa-sliders"


class ProductAdmin(ModelView, model=Product):
    column_list = [Product.id]
    form_excluded_columns = [Product.created_at, Product.updated_at]
    name = "Товар"
    name_plural = "Товары"
    icon = "fa-solid fa-sliders"


class ProductsCategoryAdmin(ModelView, model=ProductsCategory):
    column_list = [ProductsCategory.id]
    form_excluded_columns = [ProductsCategory.created_at, ProductsCategory.updated_at]
    name = "Категория товаров"
    name_plural = "Категории товаров"
    icon = "fa-solid fa-sliders"


class FavoriteAdmin(ModelView, model=Favorite):
    column_list = [Favorite.id]
    form_excluded_columns = [Favorite.created_at, Favorite.updated_at]
    name = "Избранное"
    name_plural = "Избранные"
    icon = "fa-solid fa-sliders"


class BasketAdmin(ModelView, model=Basket):
    column_list = [Basket.id]
    form_excluded_columns = [Basket.created_at, Basket.updated_at]
    name = "Корзина"
    name_plural = "Корзины"
    icon = "fa-solid fa-sliders"


class OrderAdmin(ModelView, model=Order):
    column_list = [Order.id]
    form_excluded_columns = [Order.created_at, Order.updated_at]
    name = "Заказ"
    name_plural = "Заказы"
    icon = "fa-solid fa-sliders"


class ClientAddressAdmin(ModelView, model=ClientAddress):
    column_list = [ClientAddress.id]
    form_excluded_columns = [ClientAddress.created_at, ClientAddress.updated_at]
    name = "Адреса клиента"
    name_plural = "Адреса клиентов"
    icon = "fa-solid fa-sliders"
