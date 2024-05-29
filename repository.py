import hashlib
import jwt
import random
import string

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple, List

from sqlalchemy import select, func, Row, RowMapping, cast, Float
from sqlalchemy.orm import joinedload

from models import Client, Company, Review, Story, Category, Coupon, Tariff, SubscribedTariff, Referral, \
    Reward, City, Exchange, Notification, Competition, Prize, Ticket, Task, TransactionCompetition, Question
from db import new_session
from schemas import SendPhoneNumberIn, SendPhoneNumberOut, VerifySMSDataIn, VerifySMSDataOut, PasswordData, LoginData, \
    CompanyModel, ReviewCreate, ReviewCreateMessage, ClientOut, CategoryCompanies, \
    GetSubscribedTariffs, TariffModel, AssociateTariff, AssociateTariffOut, ExchangeCreateIn, \
    AssociateCompany, UpdateExchange, NotifyData

from utils.calculate_cashback import calculate_cashback
from utils.calculate_max_balls import calculate_max_balls
from utils.calculate_reward import calculate_reward
from utils.exchange_utils import has_enough_balls_in_company, has_enough_cash, has_enough_saveup, \
    from_taker_in_holder_balls, from_holder_in_taker_cash_or_up, from_holder_in_taker_balls, \
    from_taker_in_holder_cash_or_up
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
                                    tariff=tariff, referral_link=referral_link)
                session.add(new_client)
                new_user = True

                if referral_code:
                    await process_referral(referral_code, new_client, session)
            else:
                client.token = token
                client.sms_code = sms_code
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
            return client is not None

    # Восстановление пароля еще нужно сделать

    # Отправка смс через сервис
    # def send_sms(phone, temporary_password):
    #     api_key = '0FD5185C-BEB2-466C-4CAD-21C2FEE5F855'  # Замените на ваш API-ключ SMS.RU
    #     sender = 'SaveUp'  # Замените на имя отправителя, зарегистрированное в SMS.RU
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
            result = await session.execute(select(Client).filter_by(token=authorization))
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

            if client:
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
            if companies:
                return companies
            else:
                return None


class CompanyRepository:
    @classmethod
    async def get_all_companies(cls):
        async with new_session() as session:
            result = await session.execute(select(Company).options(joinedload(Company.category)))
            return result.scalars().all()

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
            result = await session.execute(select(Coupon))
            coupons = result.scalars().all()
            for coupon in coupons:
                coupon.category = coupon.company_category.name

            return coupons


class StoryRepository:
    @classmethod
    async def get_stories_search(cls):
        async with new_session() as session:
            result = await session.execute(select(Story).where(Story.show_in_search == True))
            return result.scalars().all()

    @classmethod
    async def get_all_stories(cls):
        async with new_session() as session:
            result = await session.execute(select(Story))
            return result.scalars().all()


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
            return result.scalars().all()


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

                    result = await session.execute(select(Referral).where(Referral.referred == current_referral_agent, Referral.level == '1'))
                    current_referral = result.scalars().first()
                    if current_referral:
                        current_referral_client = current_referral_agent
                        current_referral_agent = current_referral.referrer
                        reward_percentage *= 2
                    else:
                        break
                break

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

            # client = result.scalars().first()
            # print('client_id: ', client_id)
            # print('available: ', available)
            # print('city: ', city)

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
        async with (new_session() as session):
            if data.date:
                created_on_datetime = datetime.strptime(data.date, "%a, %d %b %Y %H:%M:%S %Z")
            else:
                created_on_datetime = datetime.strptime("Thu, 01 Mar 2000 00:00:00 GMT", "%a, %d %b %Y %H:%M:%S %Z")

            if data.is_read == "true":
                result = await session.execute(select(Notification).where(Notification.client_id == data.client_id))
                notifications = result.scalars().all()

                for notification in notifications:
                    if notification.type == data.type_notify and notification.created_on.date() == created_on_datetime.date():
                        notification.read = True
                        await session.commit()

            # ---//---
            if data.is_read == "false":
                result = await session.execute(select(Notification).where(Notification.client_id == data.client_id))
                notification = result.scalars().all()

                for notification_one in notification:
                    notification_one.read = False
                    await session.commit()
            # ---//---
            result = await session.execute(select(Notification).where(Notification.client_id == data.client_id))
            notification = result.scalars().all()

            return {"notifications": notification}


class CompetitionRepository:
    @classmethod
    async def all_competitions(cls):
        async with new_session() as session:
            result = await session.execute(select(Competition).where(Competition.date_end > datetime.today()))
            competitions = result.scalars().all()
            return competitions

    @classmethod
    async def all_prizes(cls):
        async with new_session() as session:
            result = await session.execute(select(Prize).join(Prize.competition)
                                           .where(Competition.date_end > datetime.utcnow())
                                           .options(joinedload(Prize.competition)))
            prizes = result.scalars().all()
            return prizes

    @classmethod
    async def my_tickets(cls, client_id: int):
        async with new_session() as session:
            result = await session.execute(
                select(Ticket)
                .join(Ticket.client)
                .where(Client.id == client_id)
                .options(joinedload(Ticket.competition))
            )
            tickets = result.scalars().all()

            competitions_dict = {}
            for ticket in tickets:
                competition = ticket.competition
                if competition.id not in competitions_dict:
                    competitions_dict[competition.id] = {
                        "name_competition": competition.name,
                        "date_end": competition.date_end,
                        "tickets": []
                    }
                competitions_dict[competition.id]["tickets"].append({
                    "id": ticket.id,
                    "name": ticket.name,
                    "color": ticket.color,
                    "created_at": ticket.created_at,
                    "updated_at": ticket.updated_at
                })

            competitions_list = list(competitions_dict.values())

            return competitions_list

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
    async def all_tasks(cls):
        async with new_session() as session:
            result = await session.execute(select(Task))
            tasks = result.scalars().all()
            return tasks

    @classmethod
    async def all_transaction_tasks(cls):
        async with new_session() as session:
            result = await session.execute(select(TransactionCompetition))
            transaction_tasks = result.scalars().all()
            return transaction_tasks

    @classmethod
    async def all_questions(cls):
        async with new_session() as session:
            result = await session.execute(select(Question))
            questions = result.scalars().all()
            return questions
