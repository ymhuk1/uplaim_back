import hashlib
import re
from typing import List, Optional, Dict, Type

import jwt
import random
import string

from datetime import datetime, timedelta

from sqlalchemy import select, func, cast, Float, and_, desc, distinct, update, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from models import Tariff, Client, Reward, City, PaymentMethod, Coupon, Company, Review, Story, Category, \
    SubscribedTariff, Referral, Exchange, Competition, Ticket, Prize, TransactionCompetition, Task, Question, Franchise, \
    Notification, Favorite, Product, ProductsCategory, Basket, product_baskets, ClientAddress
from utils.tasks import check_tasks
from schemas import SendPhoneNumberIn, SendPhoneNumberOut, VerifySMSDataIn, VerifySMSDataOut, PasswordData, LoginData, \
    CompanyModel, ClientEditDataIn, AssociateCompany, ReviewCreate, ReviewCreateMessage, CategoryCompanies, \
    GetSubscribedTariffs, TariffModel, AssociateTariff, AssociateTariffOut, ExchangeCreateIn, UpdateExchange, \
    NotifyData, FranchiseData, DeliveryCompanies, FavoritesInDelivery, DeliveryCompany, AddProductInBasket, AddAddress

from utils.calculate_cashback import calculate_cashback
from utils.calculate_max_balls import calculate_max_balls
from utils.calculate_reward import calculate_reward
from utils.exchange_utils import *
from utils.notifications import notify
from utils.referral_chain import process_referral
from utils.transactions import get_balance, get_up_balance

# Параметры для JWT
TOKEN = "your_secret_token"


def generate_string(length):
    all_symbols = string.ascii_uppercase + string.digits
    result = ''.join(random.choice(all_symbols) for _ in range(length))
    return result


class ClientRepository:
    @classmethod
    async def send_phone_number(cls, client: SendPhoneNumberIn) -> SendPhoneNumberOut:
        async with new_session() as session:
            phone = client.phone
            device = client.device
            referral_code = client.referral_code
            push_token = client.push_token
            token_data = {'device': device, 'phone': phone}
            token = jwt.encode(token_data, TOKEN, algorithm='HS256')

            result = await session.execute(select(Tariff).where(Tariff.id == 1))
            if result:
                tariff = result.scalars().first()
                default_datetime = datetime.now()
            else:
                tariff = None
                default_datetime = None

            # Здесь будет код для отправки смс из сервиса отправки смс
            sms_code = "1111"
            # -- // --

            result = await session.execute(select(Client).filter_by(phone=phone))
            client = result.scalars().first()

            if client is None:
                referral_link = generate_string(8)
                repeat = True
                while repeat:
                    repeat_result = await session.execute(select(Client).filter_by(referral_link=referral_link))
                    repeat = repeat_result.scalars().first()
                    if repeat:
                        referral_link = generate_string(8)
                new_client = Client(phone=phone, sms_code=sms_code, token=token, tariff_start=default_datetime,
                                    tariff=tariff, referral_link=referral_link, push_token=push_token)
                session.add(new_client)
                new_user = True

                if referral_code:
                    await process_referral(referral_code, new_client, session)

            else:
                client.token = token
                client.sms_code = sms_code
                client.push_token = push_token
                new_user = False

            await session.commit()

        return {"phone": phone, "message": "SMS code sent", "token": token, "new_user": new_user}

    @classmethod
    async def verify_sms_code(cls, data: VerifySMSDataIn) -> VerifySMSDataOut:
        async with new_session() as session:
            sms_code = str(data.sms_code)
            token = data.token
            data = await session.execute(select(Client).filter_by(sms_code=sms_code, token=token))
            client = data.scalars().first()
            return client is not None

    @classmethod
    async def create_password(cls, data: PasswordData) -> bool:
        async with new_session() as session:
            result = await session.execute(select(Client).filter_by(token=data.token))
            client = result.scalars().first()
            if client:
                password_hash = hashlib.sha256(data.password.encode()).hexdigest()
                client.password = password_hash
                await session.commit()
                return True
            return False

    @classmethod
    async def login(cls, data: LoginData) -> bool:
        async with new_session() as session:
            password_hash = hashlib.sha256(data.password.encode()).hexdigest()
            result = await session.execute(select(Client).filter_by(password=password_hash, token=data.token))
            client = result.scalars().first()
            await check_tasks(session, 'login', client=client)
            return client is not None

    # Восстановление пароля еще нужно сделать
    # Отправка смс через сервис
    # def send_sms(phone, temporary_password):
    #     api_key = '0FD5185C-BEB2-466C-4CAD-21C2FEE5F855'  # Замените на ваш API-ключ SMS.RU
    #     sender = 'Uplaim'  # Замените на имя отправителя, зарегистрированное в SMS.RU
    #     message = f'Ваш временный пароль: {temporary_password}'
    #
    #     url = 'https://sms.ru/sms/send'
    #     params = {
    #         'api_id': api_key,
    #         'to': phone,
    #         'msg': message,
    #         'json': 1,
    #         'from': sender
    #     }
    #
    #     response = requests.get(url, params=params)
    #     data = response.json()
    #

    @classmethod
    async def get_client(cls, authorization: str):
        async with (new_session() as session):
            result = await session.execute(select(Client).where(Client.token == authorization))
            client = result.scalars().first()
            if client:
                balance = await get_balance(client.id)
                up_balance = await get_up_balance(client.id)
                client.balance = balance
                client.up_balance = up_balance

                result = await session.execute(select(Reward).where(Reward.agent_id == client.id))
                value = result.scalars().first()
                if value:
                    total_value = (
                        await session.execute(func.sum(cast(Reward.amount, Float) / cast(Reward.duration, Float)))
                        .filter_by(agent_id=client.id)
                        .scalar()
                    )
                else:
                    total_value = 0

                reward_in_day = total_value
                client.reward_in_day = reward_in_day

                return {'client': client}

            else:
                return None

    @classmethod
    async def get_client_companies(cls, authorization: str) -> List[CompanyModel] | None:
        async with new_session() as session:
            result = await session.execute(select(Client).where(Client.token == authorization))
            client = result.scalars().first()
            if client:
                companies = client.companies
                for company in companies:
                    company.external_links = []
                    company.cashback = {
                        "cashback": company.cashback_company
                    }
            if companies:
                return companies
            else:
                return None

    @classmethod
    async def edit_client(cls, data: ClientEditDataIn, authorization: str):
        async with new_session() as session:
            result = await session.execute(select(Client).where(Client.token == authorization))
            client = result.scalars().first()

            result = await session.execute(select(City).where(City.name == data.city))
            city = result.scalars().first()

            if client:
                if data.name: client.name = data.name
                if data.last_name: client.last_name = data.last_name
                if data.phone: client.phone = data.phone
                if data.email: client.email = data.email
                if data.gender: client.gender = data.gender
                if data.date_of_birth:
                    date_obj = datetime.strptime(data.date_of_birth, '%d-%m-%Y').date()
                    client.date_of_birth = date_obj
                if data.city and city: client.city = city

                if data.payment_methods:
                    new_payment_methods = PaymentMethod(
                        method_type=data.payment_methods.method_type,
                        client=client,
                        card_number=data.payment_methods.card_number,
                        expiry_data=data.payment_methods.expiry_data,
                        cvv=data.payment_methods.cvv,
                        sbp_phone=data.payment_methods.sbp_phone,
                        bik=data.payment_methods.bik,
                        visible=data.payment_methods.visible,
                        is_primary=data.payment_methods.is_primary,
                    )
                    session.add(new_payment_methods)

                await session.commit()

                return client
            else:
                return None

    @classmethod
    async def get_coupons_categories(cls, category_id: int, client_id: int):
        async with new_session() as session:
            coupons = (await session.execute(select(Coupon).join(Company).where(Company.category_id == category_id,
                                                                                Coupon.client_id == client_id))).scalars().all()

            return coupons

    @classmethod
    async def get_transactions(cls, client_id: int, balls: bool, cash: bool, up: bool):
        async with new_session() as session:
            list_transaction = (
                await session.execute(select(Transaction).where(Transaction.client_id == client_id))).scalars().all()
            list_balls = (await session.execute(select(Balls).where(Balls.client_id == client_id))).scalars().all()
            transactions = []
            if cash:
                for transaction in list_transaction:
                    if transaction.balance > 0:
                        transactions.append(transaction)
            elif up:
                for transaction in list_transaction:
                    if transaction.up_balance > 0:
                        transactions.append(transaction)
            elif balls:
                for transaction in list_balls:
                    if transaction.ball > 0:
                        transactions.append(transaction)

            return transactions

    @classmethod
    async def get_cities(cls):
        async with new_session() as session:
            list_cities = (await session.execute(select(City))).scalars().all()
            return list_cities


class CompanyRepository:
    @classmethod
    async def get_all_companies(cls):
        async with (new_session() as session):
            result = await session.execute(select(Company).options(joinedload(Company.category)))
            companies = result.scalars().all()

            for company in companies:
                company.external_links = []
                company.another_photo = []
                company.cashback = {
                    "cashback": company.cashback_company
                }

            return companies

    @classmethod
    async def get_company(cls, company_id: int, token: Optional[str]) -> CompanyModel | None:
        async with new_session() as session:
            reviews_rating = await session.execute(
                select(func.avg(Review.rating)).where(Review.company_id == company_id))
            reviews_rating = reviews_rating.scalar()

            company = await session.execute(
                select(Company).where(Company.id == company_id).options(joinedload(Company.category)))

            company = company.scalars().first()
            if company:
                company.another_photo = []

                for i in range(1, 6):
                    photo_attr = f'dop_photo_{i}'
                    photo_value = getattr(company, photo_attr, None)
                    if photo_value:
                        company.another_photo.append({"id": i, "photo": photo_value})

                company.external_links = []
                dict_links = {}
                for i in range(1, 6):
                    link_attr = f'link_{i}'
                    link_value = getattr(company, link_attr, None)
                    if link_value:
                        dict_links[f'link_{i}'] = link_value
                if dict_links:
                    company.external_links.append(dict_links)

                if reviews_rating:
                    company.reviews_rating = reviews_rating

                if token:
                    client = await session.execute(select(Client).where(Client.token == token))
                    client = client.scalars().first()
                    if client:
                        tariff = client.tariff
                        company.max_pay_point = await calculate_max_balls(tariff, company, session)
                        company.cashback = await calculate_cashback(tariff, company, session)

                company.news.sort(key=lambda news: news.created_at, reverse=True)

                for coupon in company.coupons:
                    coupon.category = coupon.company_category.name

                return company
            else:
                return None

    @classmethod
    async def associate_company(cls, data: AssociateCompany) -> bool | None:
        async with new_session() as session:
            result = await session.execute(select(Client).where(Client.id == data.client_id))
            client = result.scalars().first()

            result = await session.execute(select(Company).where(Company.id == data.company_id))
            company = result.scalars().first()
            if company.welcome_balls:
                added_welcome_balls = Balls(company_id=company.id, ball=int(company.welcome_balls), hide_ball=0)
                client.balls.append(added_welcome_balls)

            await check_tasks(session, 'join', company, client)

            if not client or not company:
                return False
            else:
                client.companies.append(company)
                await session.commit()
                return True

    @classmethod
    async def create_review(cls, data: ReviewCreate) -> ReviewCreateMessage:
        async with new_session() as session:

            client = await session.get(Client, data.client_id)
            company = await session.get(Company, data.company_id)
            review = await session.execute(
                select(Review).filter_by(client_id=data.client_id, company_id=data.company_id))
            review = review.scalars().first()

            if not client:
                return {"message": "Клиент с указанным ID не найден", "status": "error"}
            elif not company:
                return {"message": "Компания с указанным ID не найдена", "status": "error"}
            elif review:
                return {"message": "Вы уже оставляли отзыв", "status": "error"}
            else:
                review = Review(
                    client_id=data.client_id,
                    company_id=data.company_id,
                    rating=data.rating,
                    advantages=data.advantages,
                    disadvantages=data.disadvantages,
                    comment=data.comment
                )
                session.add(review)
                await session.commit()
                return {"message": "Отзыв успешно создан", "status": "success"}

    @classmethod
    async def search_companies(cls, search_term: str):
        async with new_session() as session:
            if search_term:
                result = await session.execute(
                    select(Company).where(Company.name.ilike(f'%{search_term}%')))
                return result.scalars().all()
            else:
                result = await session.execute(select(Company))
                return result.scalars().all()

    @classmethod
    async def get_coupons(cls):
        async with new_session() as session:
            result = await session.execute(select(Coupon).where(Coupon.client == None))
            coupons = result.scalars().all()
            for coupon in coupons:
                coupon.category = coupon.company_category.name

            return coupons

    @classmethod
    async def add_coupon(cls, coupon_id: int, authorization: str):
        async with new_session() as session:
            result = await session.execute(select(Client).where(Client.token == authorization))
            client = result.scalars().first()
            result = await session.execute(select(Coupon).where(Coupon.id == coupon_id))
            coupon = result.scalars().first()
            balance = await get_up_balance(client.id)

            if not client and not coupon:
                return None

            if coupon.price:
                if balance > coupon.price:
                    coupon.client = client
                    new_transaction = Transaction(client=client, balance=0, up_balance=coupon.price,
                                                  transaction_type='withdraw', status='success')
                    session.add(new_transaction)
                    await notify(client, 'coupon', f'Вы приобрели купон за {coupon.price} Up')

                else:
                    return {"message": "У вас не хватает UP"}
            else:
                coupon.client = client
            await session.commit()

            return {"message": "Вы успешно приобрели купон"}


class StoryRepository:
    @classmethod
    async def get_stories_search(cls):
        async with new_session() as session:
            stories_in_search = (await session.execute(
                select(Story).where(Story.show_in_search == True).order_by(desc(Story.created_at)))).scalars().all()
            return stories_in_search

    @classmethod
    async def get_all_stories(cls):
        async with new_session() as session:
            stories = (await session.execute(select(Story).order_by(desc(Story.created_at)))).scalars().all()
            return stories


class CategoryRepository:
    @classmethod
    async def get_all_categories(cls):
        async with new_session() as session:
            result = await session.execute(select(Category))
            return result.scalars().all()

    @classmethod
    async def get_company_categories(cls, data: CategoryCompanies) -> list[CompanyModel] | None:
        async with new_session() as session:
            result = await session.execute(select(Company).where(Company.category_id == data.category_id))
            companies = result.scalars().all()
            for company in companies:
                company.external_links = []
                company.another_photo = []
            return companies


class TariffRepository:
    @classmethod
    async def get_all_tariffs(cls):
        async with new_session() as session:
            result = await session.execute(select(Tariff).where(Tariff.for_client == True, Tariff.visible == True))
            return result.scalars().all()

    @classmethod
    async def get_subscriptions(cls, data: GetSubscribedTariffs) -> list[TariffModel]:
        async with new_session() as session:
            result = await session.execute(select(SubscribedTariff).where(SubscribedTariff.tariff_id == data.tariff_id))
            return result.scalars().all()

    @classmethod
    async def associate_tariff(cls, data: AssociateTariff) -> AssociateTariffOut | None:
        async with new_session() as session:
            result = await session.execute(select(Client).where(Client.id == data.client_id))
            client = result.scalars().first()
            result = await session.execute(select(Tariff).where(Tariff.id == data.tariff_id))
            tariff = result.scalars().first()
            result = await session.execute(
                select(SubscribedTariff).where(SubscribedTariff.id == data.subscribed_tariff_id))
            subscribed_tariff = result.scalars().first()

            if not client or not tariff or not subscribed_tariff:
                return None

            client.tariff = tariff
            # print('client: ', client)
            # print('tariff: ', tariff)

            client.tariff_start = datetime.today()
            client.tariff_end = client.tariff_start + timedelta(int(subscribed_tariff.duration))
            client.tariff_day = subscribed_tariff.duration

            result = await session.execute(
                select(Referral).where(Referral.referred_id == data.client_id, Referral.level == '1'))
            current_referral = result.scalars().first()
            while current_referral:
                current_referral_agent = current_referral.referrer
                current_referral_client = client

                reward_percentage = 1.0

                for _ in range(5):

                    amount_reward = subscribed_tariff.price * ((int(client.tariff.reward) / 100) / reward_percentage)

                    if amount_reward:
                        new_reward = Reward(client=current_referral_client, agent=current_referral_agent, tariff=tariff,
                                            amount=amount_reward, duration=int(subscribed_tariff.duration))
                        session.add(new_reward)

                    # await session.commit()

                    result = await session.execute(
                        select(Referral).where(Referral.referred == current_referral_agent, Referral.level == '1'))
                    current_referral = result.scalars().first()
                    if current_referral:
                        current_referral_client = current_referral_agent
                        current_referral_agent = current_referral.referrer
                        reward_percentage *= 2
                    else:
                        break
                break
            await check_tasks(session, 'tariff', client=client, tariff=tariff)

            await session.commit()
            await session.close()

            return {"message": "Tariff associated with client", "status": "success"}


class ExchangeRepository:
    @classmethod
    async def my_balls(cls, category: Optional[str], city: Optional[str], token: str):
        async with new_session() as session:
            if token is None:
                return {"error": "Authorization token not provided"}
            result = await session.execute(select(Client).where(Client.token == token))
            client = result.scalars().first()
            if client is None:
                return {"error": "Client not found"}

            balls_data = []
            for ball_info in client.balls:
                if ball_info.ball > 0:

                    result = await session.execute(select(Company).where(Company.id == ball_info.company_id))
                    company = result.scalars().first()

                    if ((not category or (company and company.categories and company.categories.name == category)) and
                            (not city or (company and company.city and company.city.name == city))):
                        ball_data = {
                            "balls": ball_info.ball,
                            "company_id": ball_info.company_id,
                            "company_name": company.name if company else None,
                            "company_logo": company.main_photo if company else None
                        }

                        balls_data.append(ball_data)

                return {"balls": balls_data}

    @classmethod
    async def all_companies(cls, city: Optional[str], category: Optional[str]):
        async with new_session() as session:

            companies_query = await session.execute(select(Company))

            if city:
                companies_query = await session.execute(select(Company).where(Company.city.has(name=city)))
            if category:
                companies_query = await session.execute(select(Company).where(Company.category.has(name=category)))

            companies = companies_query.scalars().all()

            companies_data = [
                {"id": company.id, "name": company.name, "photo": company.main_photo} for company in companies
            ]
            return {"companies": companies_data}

    @classmethod
    async def all_cities(cls):
        async with new_session() as session:
            result = await session.execute(select(City))
            cities = result.scalars().all()

            cities_data = [
                {"id": city.id, "name": city.name} for city in cities
            ]
            return {"cities": cities_data}

    @classmethod
    async def all_categories(cls):
        async with new_session() as session:
            result = await session.execute(select(Category))
            categories = result.scalars().all()

            categories_data = [
                {"id": category.id, "name": category.name, "photo": category.icon, "color": category.color} for category
                in
                categories
            ]
            return {"categories": categories_data}

    @classmethod
    async def active_exchange(cls, client_id: int, available: bool, city: Optional[str]):
        async with new_session() as session:

            result = await session.execute(
                select(Exchange).where(Exchange.status == 'active', Exchange.taker_id.is_(None)))
            active_exchanges = result.scalars().all()

            if available:
                if client_id is None:
                    return {"error": "client_id must be provided as a query parameter"}
                result = await session.execute(
                    select(Exchange).where(Exchange.status == 'active', Exchange.taker_id.is_(None),
                                           Exchange.holder_id != client_id))
                active_exchanges = result.scalars().all()

            if city != "Все":
                active_exchanges = [active_exchange for active_exchange in active_exchanges if
                                    active_exchange.city_deal == city]

            filtered_exchanges = []
            if available:
                result = await session.execute(select(Client).where(Client.id == client_id))
                client = result.scalars().first()
                for exchange in active_exchanges:
                    if exchange.holder_company_id and exchange.get_balls:
                        if await has_enough_balls_in_company(client, exchange.holder_company_id, exchange.get_balls):
                            filtered_exchanges.append(exchange)
                    elif exchange.get_saveup:
                        if await has_enough_saveup(client, exchange.get_saveup):
                            filtered_exchanges.append(exchange)
                    elif exchange.get_cash:
                        if await has_enough_cash(client, exchange.get_cash):
                            filtered_exchanges.append(exchange)

            if available:
                my_exchanges = filtered_exchanges
            else:
                my_exchanges = active_exchanges

            return {"exchange": my_exchanges}

    @classmethod
    async def proposed_exchange(cls, taker_id: int):
        async with new_session() as session:
            result = await session.execute(
                select(Exchange).where(Exchange.status == 'active', Exchange.taker_id == taker_id))
            proposed_exchange = result.scalars().all()
            return {"exchange": proposed_exchange}

    @classmethod
    async def create(cls, data: ExchangeCreateIn):
        async with new_session() as session:
            result = await session.execute(select(Client).where(Client.id == data.holder_id))
            client = result.scalars().first()
            if not client:
                return {"error": "Клиент не найден"}

            holder_company_id = data.holder_company_id if data.holder_company_id else None

            if data.taker_categories:
                result = await session.execute(select(Category).where(Category.id.in_(data.taker_categories)))
                taker_categories = result.scalars().all()
            else:
                taker_categories = []

            if data.taker_companies is not None:
                result = await session.execute(select(Category).where(Category.id.in_(data.taker_companies)))
                taker_companies = result.scalars().all()
            else:
                taker_companies = []

            allowed_type_deal = ['buy', 'sell', 'exchange_sell', 'exchange']
            if data.type_deal not in allowed_type_deal:
                return {"error": f"Некорректный тип сделки. Разрешенные типы: {', '.join(allowed_type_deal)}"}
            required_fields = []
            if data.type_deal == 'buy':
                required_fields.append('get_balls')
                if data.taker_companies:
                    required_fields.append('taker_companies')
                elif data.taker_categories:
                    required_fields.append('taker_categories')
                else:
                    required_fields.append('taker_companies') or required_fields.append('taker_categories')

                if data.give_saveup:
                    required_fields.append('give_saveup')
                    if not await has_enough_saveup(data.holder_id, data.give_saveup):
                        return {"error": "У вас не достаточно UP"}
                elif data.give_cash:
                    required_fields.append('give_cash')
                    if not await has_enough_cash(data.holder_id, data.give_cash):
                        return {"error": "У вас не достаточно денег"}
                else:
                    required_fields.append('give_saveup') or required_fields.append('give_cash')
            elif data.type_deal == 'sell':
                required_fields.append('give_balls')
                required_fields.append('holder_company_id')
                if data.holder_company_id:
                    if not await has_enough_balls_in_company(data.holder_id, data.holder_company_id, data.give_balls):
                        return {"error": "У вас не достаточно баллов в выбранной компании"}
                if data.get_saveup:
                    required_fields.append('get_saveup')
                elif data.get_cash:
                    required_fields.append('get_cash')
                else:
                    required_fields.append('get_saveup') or required_fields.append('get_cash')
            elif data.type_deal == 'exchange_sell':
                required_fields.append('give_balls')
                required_fields.append('holder_company_id')
                if data.holder_company_id:
                    if not await has_enough_balls_in_company(data.holder_id, data.holder_company_id, data.give_balls):
                        return {"error": "У вас не достаточно баллов в выбранной компании"}
                if data.get_balls:
                    required_fields.append('get_balls')
                    if data.taker_companies:
                        required_fields.append('taker_companies')
                    elif data.taker_categories:
                        required_fields.append('taker_categories')
                    else:
                        required_fields.append('taker_companies') or required_fields.append('taker_categories')
                else:
                    required_fields.append('get_balls')
                if data.get_saveup:
                    required_fields.append('get_saveup')
                elif data.get_cash:
                    required_fields.append('get_cash')
                else:
                    required_fields.append('get_saveup') or required_fields.append('get_cash')
            elif data.type_deal == 'exchange':
                required_fields.append('give_balls')
                required_fields.append('get_balls')
                if data.taker_companies:
                    required_fields.append('taker_companies')
                elif data.taker_categories:
                    required_fields.append('taker_categories')
                else:
                    required_fields.append('taker_companies') or required_fields.append('taker_categories')
                required_fields.append('holder_company_id')
                if data.holder_company_id:
                    if not await has_enough_balls_in_company(data.holder_id, data.holder_company_id, data.give_balls):
                        return {"error": "У вас не достаточно баллов в выбранной компании"}

            missing_fields = [field for field in required_fields if not data.__dict__.get(field)]
            if missing_fields:
                return {"error": f"Не заполненные обязательные поля: {', '.join(missing_fields)}"}

            status = data.status if data.status else 'active'
            last_holder_id = data.last_holder_id if data.last_holder_id else None
            city_deal = data.city_deal if data.city_deal else None
            counter_deal = data.counter_deal if data.counter_deal else False
            partial_deal = data.partial_deal if data.partial_deal else False

            new_exchange = Exchange(holder_id=data.holder_id, last_holder_id=last_holder_id,
                                    holder_company_id=holder_company_id,
                                    taker_companies=taker_companies, taker_categories=taker_categories,
                                    counter_deal=counter_deal,
                                    type_deal=data.type_deal, city_deal=city_deal, partial_deal=partial_deal,
                                    give_balls=data.give_balls,
                                    get_balls=data.get_balls, give_saveup=data.give_saveup, get_saveup=data.get_saveup,
                                    give_cash=data.give_cash,
                                    get_cash=data.get_cash, status=status)

            session.add(new_exchange)
            await session.commit()

            return {"exchange": new_exchange}

    @classmethod
    async def update_exchange(cls, exchange_id: int, data: UpdateExchange):
        async with new_session() as session:

            # print('exchange_id: ', exchange_id)
            # print('data: ', data)

            result = await session.execute(select(Exchange).where(Exchange.id == exchange_id))
            existing_exchange = result.scalars().first()
            if not existing_exchange:
                return {"error": "Сделка не найдена"}

            fields_to_update = ['taker_id', 'holder_company_id', 'holder_category_id',
                                'counter_deal', 'partial_deal', 'type_deal', 'city_deal', 'give_balls', 'get_balls',
                                'give_saveup', 'get_saveup', 'give_cash', 'get_cash', 'status']

            for field in fields_to_update:
                if hasattr(data, field):
                    setattr(existing_exchange, field, getattr(data, field))

            if data.taker_companies:
                existing_exchange.taker_companies.clear()
                existing_exchange.taker_categories.clear()

                selected_taker_companies = data['taker_companies']
                taker_companies = Company.query.filter(Company.id.in_(selected_taker_companies)).all()
                existing_exchange.taker_companies = taker_companies

            if data.taker_categories:
                existing_exchange.taker_companies.clear()
                existing_exchange.taker_categories.clear()

                selected_taker_categories = data['taker_categories']
                taker_categories = Category.query.filter(Category.id.in_(selected_taker_categories)).all()
                existing_exchange.taker_categories = taker_categories

            existing_exchange.updated_on = datetime.utcnow()

            await session.commit()

            return {"exchange": existing_exchange}

    @classmethod
    async def accept_exchange(cls, exchange_id: int, taker_id: int, taker_company_id: int):
        async with new_session() as session:
            result = await session.execute(select(Exchange).where(Exchange.id == exchange_id))
            existing_exchange = result.scalars().first()

            if not existing_exchange:
                return {"error": "Сделка не найдена"}

            if not existing_exchange != 'active':
                return {"error": "Нельзя принять сделку в данном статусе"}

            existing_exchange.taker_id = taker_id
            existing_exchange.taker_company_id = taker_company_id
            existing_exchange.status = 'completed'

            result = await session.execute(select(Client).where(Client.id == existing_exchange.holder_id))
            holder = result.scalars().first()

            result = await session.execute(select(Client).where(Client.id == taker_id))
            taker = result.scalars().first()

            if not holder or not taker:
                return {"error": "Не указан клиент"}

            type_deal = existing_exchange.type_deal

            if type_deal == 'buy':
                holder_balls, taker_balls, error = await from_taker_in_holder_balls(holder, taker, taker_company_id,
                                                                                    existing_exchange)

                if error:
                    return error
                error = await from_holder_in_taker_cash_or_up(holder, taker, existing_exchange, session)
                if error:
                    return error

            elif type_deal == 'sell' or type_deal == 'exchange_sell' and not taker_company_id:
                holder_balls, taker_balls, error = await from_holder_in_taker_balls(holder, taker, existing_exchange)
                if error:
                    return error
                error = await from_taker_in_holder_cash_or_up(holder, taker, existing_exchange, session)
                if error:
                    return error

            elif type_deal == 'exchange' or type_deal == 'exchange_sell' and taker_company_id:
                holder_balls, taker_balls, error = await from_taker_in_holder_balls(holder, taker, taker_company_id,
                                                                                    existing_exchange)
                if error:
                    return error
                holder_balls, taker_balls, error = await from_holder_in_taker_balls(holder, taker, existing_exchange)
                if error:
                    return error
            else:
                return {"error": "Не указан тип сделки"}

            await notify(existing_exchange.holder_id, 'exchange', 'Ваша сделка закрыта')
            await check_tasks(session, 'exchange', client=taker)

            return {"exchange": existing_exchange}

    @classmethod
    async def delete_exchange(cls, exchange_id: int):
        async with new_session() as session:
            result = await session.execute(select(Exchange).where(Exchange.id == exchange_id))
            existing_exchange = result.scalars().first()
            if not existing_exchange:
                return {"error": "Сделка не найдена"}

            await session.delete(existing_exchange)
            await session.commit()

            return {"message": "Сделка успешно удалена"}


class ReferralRepository:

    @classmethod
    async def list_referral(cls, client_id: int):
        async with new_session() as session:
            result = await session.execute(select(Referral).where(Referral.referrer_id == client_id))
            list_referred = result.scalars().all()

            result = await session.execute(select(Client).where(Client.id == client_id))
            client = result.scalars().first()

            level_counts = {}
            level_tariff_counts = {}

            result = (
                await session.execute(
                    select(Referral)
                    .join(Client, Referral.referred_id == Client.id)
                    # .join(Tariff, Client.tariff_id == Tariff.id)
                    .filter(
                        Referral.level == '1',
                        Referral.referrer_id == client_id,
                        # Tariff.name != 'Free'
                    )
                )
            )
            first_level_people = result.scalars().all()

            serialized_first_level_people = []

            for person in first_level_people:
                person_data = {
                    "name": person.referred.name,
                    "surname": person.referred.last_name,
                    "tariff_name": person.referred.tariff.name if person.referred.tariff else "Unknown",
                    "tariff_color": person.referred.tariff.color if person.referred.tariff else "Unknown"
                }
                serialized_first_level_people.append(person_data)
            # print('serialized_first_level_people: ', serialized_first_level_people)

            for ref in list_referred:
                level = ref.level
                level_counts[level] = level_counts.get(level, 0) + 1

                tariff = ref.referred.tariff if ref.referred.tariff else None

                if tariff:
                    tariff_name = tariff.name
                    tariff_color = tariff.color
                else:
                    tariff_name = "Unknown"
                    tariff_color = "#121123"

                level_tariff_counts.setdefault(level, {}).setdefault(tariff_name, {"count": 0, "color": tariff_color})
                level_tariff_counts[level][tariff_name]["count"] += 1

            for level in range(1, 6):
                level_str = str(level)
                level_counts.setdefault(level_str, 0)
                level_tariff_counts.setdefault(level_str, {})

            serialized_list_referred = []

            for level_str, tariffs in level_tariff_counts.items():
                if level_str == "1":
                    people = serialized_first_level_people
                else:
                    people = []
                if client.tariff:
                    if client.tariff.reward is not None:
                        reward = calculate_reward(int(client.tariff.reward), int(level_str))
                    else:
                        reward = 0
                else:
                    reward = 0
                serialized_list_referred.append({
                    "level": level_str,
                    "quantity": level_counts[level_str],
                    "tariff_counts": [
                        {"tariff": tariff, "count": data["count"], "color": data["color"]}
                        for tariff, data in tariffs.items()
                    ],
                    "reward": reward,
                    "people": people
                })

            return {"list_referred": serialized_list_referred}

    @classmethod
    async def my_reward(cls, client_id: int):
        async with new_session() as session:
            result = await session.execute(select(Reward).where(Reward.agent_id == client_id))
            value = result.scalars().first()
            if value:
                total_value = (
                    await session.execute(func.sum(cast(Reward.amount, Float) / cast(Reward.duration, Float)))
                    .filter_by(agent_id=client_id)
                    .scalar()
                )
            else:
                total_value = 0

            return {"total_value": round(total_value, 2)}


class NotificationsRepository:
    @classmethod
    async def get_notifications(cls, data: NotifyData):
        try:
            async with (new_session() as session):
                if data.date:
                    created_on_datetime = datetime.strptime(data.date, "%a, %d %b %Y %H:%M:%S %Z")
                else:
                    created_on_datetime = datetime.strptime("Thu, 01 Mar 2000 00:00:00 GMT", "%a, %d %b %Y %H:%M:%S %Z")

                # Fetch all notifications for the client
                result = await session.execute(select(Notification).where(Notification.client_id == data.client_id))
                notifications = result.scalars().all()

                if data.is_read == "true":
                    for notification in notifications:
                        if notification.type == data.type_notify and notification.created_on.date() == created_on_datetime.date():
                            notification.read = True
                    await session.commit()

                elif data.is_read == "false":
                    for notification in notifications:
                        notification.read = False
                    await session.commit()

                return {"notifications": notifications}

        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return {"error": "Database error occurred."}

        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"error": "An unexpected error occurred."}


class CompetitionRepository:
    @classmethod
    async def all_competitions(cls, client_id: int):
        async with new_session() as session:
            result = await session.execute(select(Competition).where(Competition.date_end > datetime.today()))
            competitions = result.scalars().all()

            if client_id is not None:
                for competition in competitions:
                    # Получаем количество активированных билетов для текущего клиента и соревнования
                    tickets_count_result = await session.execute(
                        select(func.count(Ticket.id))
                        .where(Ticket.competition_id == competition.id, Ticket.client_id == client_id,
                               Ticket.activate == True)
                    )
                    tickets_count = tickets_count_result.scalar()

                    # Добавляем это число в объект соревнования
                    competition.current_client_active_tickets = tickets_count

            return competitions

    @classmethod
    async def all_prizes(cls):
        async with new_session() as session:
            current_date = datetime.utcnow()

            # Perform an outer join to include competitions without prizes and filter by date_end
            result = await session.execute(
                select(Competition, Prize)
                .outerjoin(Prize, Prize.competition_id == Competition.id)
                .where(Competition.date_end > current_date)
                .options(joinedload(Prize.competition))
            )

            competitions_dict = {}
            for competition, prize in result:
                if competition.id not in competitions_dict:
                    competitions_dict[competition.id] = {
                        "name_competition": competition.name,
                        "date_end": competition.date_end,
                        "color": competition.color,
                        "prizes": []
                    }
                if prize:
                    competitions_dict[competition.id]["prizes"].append({
                        "id": prize.id,
                        "name": prize.name,
                        "description": prize.description,
                        "created_at": prize.created_at,
                        "updated_at": prize.updated_at
                    })

            competitions_list = list(competitions_dict.values())

            return competitions_list

    @classmethod
    async def my_tickets(cls, client_id: int):
        async with new_session() as session:
            current_date = datetime.now()

            # Perform an outer join to include competitions without tickets
            result = await session.execute(
                select(Competition, Ticket)
                .outerjoin(Ticket, and_(Ticket.client_id == client_id, Ticket.competition_id == Competition.id))
                .where(Competition.date_end > current_date)
                .options(joinedload(Ticket.competition))
            )

            competitions_dict = {}
            for competition, ticket in result:
                if competition.id not in competitions_dict:
                    competitions_dict[competition.id] = {
                        "name_competition": competition.name,
                        "date_end": competition.date_end,
                        "color": competition.color,
                        "tickets": []
                    }
                if ticket and ticket.activate:
                    competitions_dict[competition.id]["tickets"].append({
                        "id": ticket.id,
                        "name": ticket.name,
                        "color": ticket.color,
                        "created_at": ticket.created_at,
                        "updated_at": ticket.updated_at
                    })

            result = await session.execute(
                select(
                    Competition.id,
                    Competition.name,
                    Ticket.color,
                    func.count(Ticket.id).label('quantity_tickets')
                ).join(Ticket, Competition.id == Ticket.competition_id)
                .where(Ticket.client_id == client_id, Ticket.activate != True)
                .group_by(Competition.id, Competition.name, Ticket.color)
            )
            tickets_data = result.all()

            # Format the results into the desired structure
            not_activate_tickets = [
                {
                    "competition_id": competition_id,
                    "quantity_tickets": quantity_tickets,
                    "competition": competition_name,
                    "color": color
                }
                for competition_id, competition_name, color, quantity_tickets in tickets_data
            ]

            competitions_list = list(competitions_dict.values())

            return {
                "not_activate": not_activate_tickets,
                "activate": competitions_list
            }

    @classmethod
    async def tickets_on_sell(cls):
        async with new_session() as session:
            result = await session.execute(
                select(
                    Competition.id,
                    Competition.name,
                    Ticket.color,
                    func.count(Ticket.id).label('quantity_tickets')
                ).join(Ticket, Competition.id == Ticket.competition_id)
                .where(Ticket.client_id == None)
                .group_by(Competition.id, Competition.name, Ticket.color)
            )
            tickets_data = result.all()

            # Format the results into the desired structure
            tickets_on_sell = [
                {
                    "competition_id": competition_id,
                    "quantity_tickets": quantity_tickets,
                    "competition": competition_name,
                    "color": color
                }
                for competition_id, competition_name, color, quantity_tickets in tickets_data
            ]

            return tickets_on_sell

    @classmethod
    async def buy_tickets(cls, client_id: int, competition_id: int, quantity: int):
        async with new_session() as session:
            result = await session.execute(select(Client).where(Client.id == client_id))
            client = result.scalars().first()
            if client is None:
                return {"status": "error", "message": "Клиент не найден"}

            result = await session.execute(
                select(Ticket)
                .where(Ticket.client_id == None, Ticket.competition_id == competition_id)
                .limit(quantity)
            )
            available_tickets = result.scalars().all()

            if len(available_tickets) < quantity:
                return {"status": "error", "message": "Не достаточно билетов"}

            # Привязать билеты к клиенту
            for ticket in available_tickets:
                ticket.client_id = client_id

            await session.commit()
            return {"status": "success", "message": f'Билетов успешно куплено: {quantity} '}

    @classmethod
    async def activate_tickets(cls, client_id: int, competition_id: int, count: int):
        async with new_session() as session:
            client = (await session.execute(select(Client).where(Client.id == client_id))).scalars().first()
            if client is None:
                return {"status": "error", "message": "Клиент не найден"}
            competition = (
                await session.execute(select(Competition).where(Competition.id == competition_id))).scalars().first()
            if competition is None:
                return {"status": "error", "message": "Конкурс не найден"}
            tickets = (await session.execute(
                select(Ticket).where(
                    Ticket.competition_id == competition_id,
                    Ticket.client_id == client_id,
                    Ticket.activate == False
                ).limit(count)
            )).scalars().all()

            if len(tickets) < count:
                return {"status": "error", "message": "Недостаточно билетов"}

            for ticket in tickets:
                ticket.activate = True

            await session.commit()
            return {"status": "success", "message": f"{count} билетов активировано"}

    @classmethod
    async def all_tasks(cls):
        async with new_session() as session:
            result = await session.execute(select(Task))
            tasks = result.scalars().all()
            return tasks

    @classmethod
    async def all_transaction_tasks(cls, client_id: int):
        async with new_session() as session:
            result = await session.execute(
                select(TransactionCompetition).where(TransactionCompetition.client_id == client_id))
            transaction_tasks = result.scalars().all()
            return transaction_tasks

    @classmethod
    async def all_questions(cls):
        async with new_session() as session:
            result = await session.execute(select(Question))
            questions = result.scalars().all()
            return questions


class FranchiseRepository:
    @classmethod
    async def create_request(cls, data: FranchiseData):
        async with new_session() as session:
            franchise = Franchise(
                name=data.name,
                phone=data.phone,
            )
            session.add(franchise)
            await session.commit()
            return {"message": "Запрос принят", "status": "success"}


class DeliveryRepository:

    @classmethod
    async def get_delivery_categories(cls):
        async with new_session() as session:
            result = await session.execute(
                select(Category)
                .distinct()  # выбираем только уникальные категории
                .join(Company)  # соединяем с компаниями
                .where(Company.delivery == True)  # фильтруем компании с delivery=True
            )

            categories = result.scalars().all()
            return categories


    @classmethod
    async def get_delivery_companies(cls, data: DeliveryCompanies) -> list[CompanyModel] | None:
        async with new_session() as session:
            if data.category_id:
                companies = (await session.execute(select(Company).where(Company.category_id == data.category_id,
                                                                         Company.delivery == True))).scalars().all()
            elif data.term:
                companies = (
                    await session.execute(select(Company).where(Company.name.ilike(f'%{data.term}%')))).scalars().all()
            else:
                companies = (await session.execute(select(Company).where(Company.delivery == True))).scalars().all()

            for company in companies:
                company.external_links = []
                company.another_photo = []
            return companies

    @classmethod
    async def add_favorite(cls, data: FavoritesInDelivery) -> dict[str, str]:
        async with new_session() as session:
            if data.company_id:
                company = (
                    await session.execute(select(Company).where(Company.id == data.company_id))).scalars().first()
                if company:
                    favorite_company = Favorite(
                        client_id=data.client_id,
                        company_id=data.company_id,
                        is_company=True
                    )
                    session.add(favorite_company)
                    await session.commit()
                    return {"message": "Компания добавлена в избранное"}
                else:
                    return {"message": "Компания не найдена"}
            elif data.product_id:
                product = (
                    await session.execute(select(Product).where(Product.id == data.product_id))).scalars().first()
                if product:
                    favorite_product = Favorite(
                        client_id=data.client_id,
                        product_id=data.product_id,
                        is_product=True
                    )
                    session.add(favorite_product)
                    await session.commit()
                    return {"message": "Товар добавлен в избранное"}
                else:
                    return {"message": "Товар не найден"}
            else:
                return {"message": "Товар или компания не найдены"}

    @classmethod
    async def get_delivery_company(cls, data: DeliveryCompany):
        async with new_session() as session:

            if data.company_id:
                company = (
                    await session.execute(select(Company).where(Company.id == data.company_id))).scalars().first()

                categories = (
                    await session.execute(
                        select(ProductsCategory)
                        .distinct(ProductsCategory.id)
                        .join(Product, ProductsCategory.id == Product.category_id)
                        .where(Product.company_id == data.company_id)
                    )
                ).scalars().all()

                products = []

                if data.category_id == 0:
                    products_query = (
                        select(Product)
                        .join(Favorite, Favorite.product_id == Product.id)
                        .where(Favorite.client_id == data.client_id)
                        .where(Favorite.is_product == True)
                        .where(Product.company_id == data.company_id)
                        .options(joinedload(Product.category))
                    )
                    products = (await session.execute(products_query)).scalars().all()

                elif data.category_id:
                    products_query = (
                        select(Product)
                        .where(Product.company_id == data.company_id)
                        .where(Product.category_id == data.category_id)
                        .options(joinedload(Product.category))
                    )
                    products = (await session.execute(products_query)).scalars().all()

                else:
                    products_query = (
                        select(Product)
                        .where(Product.company_id == data.company_id)
                        .options(joinedload(Product.category))
                    )
                    products = (await session.execute(products_query)).scalars().all()

                favorite = {
                    "updated_at": "2024-08-10T22:03:38.604466",
                    "id": 0,
                    "name": "Избранное",
                    "created_at": "2024-08-10T22:03:38.604464"
                }
                categories.insert(0, favorite)

                return {
                    "company": company,
                    "products": products,
                    "categories": categories,
                }

    @classmethod
    async def add_product_in_basket(cls, data: AddProductInBasket):
        async with new_session() as session:
            client = (await session.execute(select(Client).where(Client.id == data.client_id))).scalars().first()
            product = (await session.execute(select(Product).where(Product.id == data.product_id))).scalars().first()
            company = (await session.execute(select(Company).where(Company.id == data.company_id))).scalars().first()
            basket = (await session.execute(select(Basket).where(Basket.client == client, Basket.company == company))).scalars().first()

            if not client or not product or not company:
                return False

            if basket:
                # Проверяем, есть ли уже этот продукт в корзине
                product_in_basket = (await session.execute(
                    select(product_baskets).where(product_baskets.c.basket_id == basket.id,
                                                  product_baskets.c.product_id == product.id)
                )).first()

                if product_in_basket:
                    # Увеличиваем количество продукта в корзине
                    new_quantity = int(product_in_basket.quantity) + 1
                    await session.execute(
                        update(product_baskets).where(
                            product_baskets.c.basket_id == basket.id,
                            product_baskets.c.product_id == product.id
                        ).values(quantity=str(new_quantity))
                    )
                else:
                    # Добавляем новый продукт в корзину
                    await session.execute(
                        insert(product_baskets).values(basket_id=basket.id, product_id=product.id,
                                                       quantity="1")
                    )
            else:
                # Создаем новую корзину для клиента и компании
                basket = Basket(client=client, company=company)
                session.add(basket)
                await session.flush()  # Чтобы получить ID новой корзины

                # Добавляем продукт в новую корзину
                await session.execute(
                    insert(product_baskets).values(basket_id=basket.id, product_id=product.id, quantity="1")
                )

            await session.commit()  # Сохраняем изменения
            return {"status": "success", "message": "Товар успешно добавлен"}

    @classmethod
    async def get_baskets(cls, client_id: int):
        async with new_session() as session:
            # Запрос для получения корзин клиента с продуктами, их количеством, фото, весом, названием компании и id корзины
            baskets_data = await session.execute(
                select(
                    Basket.id,
                    Company.name,
                    Product.id,
                    Product.name,
                    Product.photo,
                    Product.weight,
                    Product.price,
                    product_baskets.c.quantity
                ).join(Basket, Company.id == Basket.company_id)
                .join(product_baskets, Basket.id == product_baskets.c.basket_id)
                .join(Product, product_baskets.c.product_id == Product.id)
                .where(Basket.client_id == client_id)
            )

            baskets = {}
            for basket_id, company_name, product_id, product_name, photo, weight, product_price, quantity in baskets_data:
                if company_name not in baskets:
                    baskets[company_name] = {
                        "basket_id": basket_id,
                        "products": []
                    }
                baskets[company_name]["products"].append({
                    "product_id": product_id,
                    "product_name": product_name,
                    "photo": photo,
                    "weight": weight,
                    "price": product_price,
                    "quantity": quantity,
                })

            return baskets

    @classmethod
    async def add_address(cls, data: AddAddress):
        async with new_session() as session:
            client = (await session.execute(select(Client).where(Client.id == data.client_id))).scalars().first()
            if not client:
                return {"status": "error", "message": "Клиент не найден"}

            address_pattern = re.compile(
                r'(?P<city>\w+)'  # Город (обязательная часть)
                r'(?:,\s*(?P<street>[\w\s]+)\s*)?'  # Улица (необязательная часть)
                r'(?:,\s*(?:д\s*\.?|дом\s*\.?)?\s*(?P<house>\d+)\s*)?'  # Дом (необязательная часть)
                r'(?:,\s*(?:п\s*\.?|подъезд\s*\.?)?\s*(?P<entrance>\d+)\s*)?'  # Подъезд (необязательная часть)
                r'(?:,\s*(?:кв\s*\.?|квартира\s*\.?)?\s*(?P<flat>\d+)\s*)?'  # Квартира (необязательная часть)
            )
            match = address_pattern.match(data.address)

            if not match:
                return {"status": "error", "message": "Неправильный формат адреса"}

            address_data = match.groupdict()

            city = data.city or address_data.get('city')
            street = data.street or address_data.get('street')
            house = data.house or address_data.get('house')
            entrance = data.entrance or address_data.get('entrance')
            flat = data.flat or address_data.get('flat')

            new_address = ClientAddress(
                client_id=data.client_id,
                address=data.address,
                oksm_code="...",
                city=city,
                street=street,
                house=house,
                entrance=entrance,
                flat=flat
            )

            session.add(new_address)
            await session.commit()
            return new_address


