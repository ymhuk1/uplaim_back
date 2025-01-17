import os
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Table, Float, JSON, Date
from sqlalchemy.orm import declarative_base, relationship
from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import FileType

from config import STATIC_FOLDER, STATIC_FOLDER_CATEGORIES, STATIC_FOLDER_COMPANIES_MAIN, \
    STATIC_FOLDER_COMPANIES_ANOTHER, STATIC_FOLDER_NEWS, STATIC_FOLDER_TARIFFS, STATIC_FOLDER_STORIES_PHOTO, \
    STATIC_FOLDER_STORIES_ICON, STATIC_FOLDER_COMPETITIONS, STATIC_FOLDER_PRIZES, STATIC_FOLDER_TASKS, \
    STATIC_FOLDER_CLIENTS, STATIC_FOLDER_PRODUCTS
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("No encryption key found in environment variables")
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

storage = FileSystemStorage(path=STATIC_FOLDER + '/img')

Base = declarative_base()


company_client_link = Table(
    "company_client_link",
    Base.metadata,
    Column("client_id", ForeignKey("clients.id")),
    Column("company_id", ForeignKey("companies.id")),
)

company_tag_link = Table(
    "company_tag_link",
    Base.metadata,
    Column("tag_id", ForeignKey("tags.id")),
    Column("company_id", ForeignKey("companies.id")),
)

company_tariff_link = Table(
    'company_tariff_link',
    Base.metadata,
    Column('company_id', Integer, ForeignKey('companies.id'), primary_key=True),
    Column('tariff_id', Integer, ForeignKey('tariffs.id'), primary_key=True)
)

exchange_companies = Table(
    'exchange_companies',
    Base.metadata,
    Column('company_id', Integer, ForeignKey('companies.id'), primary_key=True),
    Column('exchange_id', Integer, ForeignKey('exchange.id'), primary_key=True)
)

exchange_categories = Table(
    'exchange_categories',
    Base.metadata,
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True),
    Column('exchange_id', Integer, ForeignKey('exchange.id'), primary_key=True)
)

competition_clients = Table(
    'competition_clients',
    Base.metadata,
    Column('competition_id', Integer, ForeignKey('competitions.id'), primary_key=True),
    Column('client_id', Integer, ForeignKey('clients.id'), primary_key=True)
)

client_tasks = Table(
    'client_tasks',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('client_id', Integer, ForeignKey('clients.id'), primary_key=True),
    Column('quantity', String),
    Column('done', String),
)

product_baskets = Table(
    'product_baskets',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('basket_id', Integer, ForeignKey('baskets.id'), primary_key=True),
    Column('quantity', String),
)

product_orders = Table(
    'product_orders',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('order_id', Integer, ForeignKey('orders.id'), primary_key=True),
    Column('quantity', String),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    last_name = Column(String)
    phone = Column(String)
    email = Column(String)
    password = Column(String)
    type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True)
    city = relationship("City")


class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return self.name


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True)
    password = Column(String, nullable=True)
    sms_code = Column(String, nullable=True)
    referral_link = Column(String, nullable=True)
    device = Column(String, nullable=True)
    token = Column(String, nullable=True)
    push_token = Column(String, nullable=True)
    photo = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_CLIENTS)), nullable=True)
    gender = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    reviews = relationship("Review", back_populates="client", lazy="subquery")

    companies = relationship('Company', secondary="company_client_link", back_populates="clients", lazy="subquery")

    balls = relationship("Balls", back_populates="client", lazy="subquery")

    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True)
    city = relationship("City", lazy="subquery")

    tariff_id = Column(Integer, ForeignKey('tariffs.id'), nullable=True)
    tariff = relationship("Tariff", lazy="subquery")
    tariff_start = Column(DateTime())
    tariff_day = Column(String(50))
    tariff_end = Column(DateTime())

    transactions = relationship('Transaction', back_populates='client', lazy="subquery")
    transaction_competitions = relationship('TransactionCompetition', back_populates='client', lazy="subquery")

    notify = relationship('Notification', back_populates='client', lazy="subquery")
    referrals = relationship('Referral', back_populates='referrer', foreign_keys='Referral.referrer_id', lazy="subquery")

    given_clients = relationship('Exchange', foreign_keys='Exchange.holder_id', back_populates='holder', lazy="subquery")
    received_clients = relationship('Exchange', foreign_keys='Exchange.taker_id', back_populates='taker', lazy="subquery")

    competitions = relationship('Competition', secondary="competition_clients", back_populates="clients", lazy="subquery")
    tasks = relationship('Task', secondary="client_tasks", back_populates="clients", lazy="subquery")
    coupons = relationship("Coupon", back_populates="client", lazy="subquery")
    payment_methods = relationship("PaymentMethod", back_populates="client", lazy="subquery")
    push = relationship('Push', back_populates='client', lazy="subquery")

    favorites = relationship("Favorite", back_populates="client")
    baskets = relationship("Basket", back_populates="client")
    orders = relationship("Order", back_populates="client")

    addresses = relationship("ClientAddress", back_populates="client")

    def __str__(self):
        return str(self.phone)


class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    id = Column(Integer, primary_key=True)
    method_type = Column(String)  # card, sbp, account?
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship("Client")
    card_number = Column(String, nullable=True)
    expiry_data = Column(String, nullable=True)
    cvv = Column(String, nullable=True)
    sbp_phone = Column(String, nullable=True)
    bik = Column(String, nullable=True)
    visible = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.method_type)


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    icon = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_CATEGORIES)), nullable=True)
    color = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    exchange_categories = relationship('Exchange', secondary="exchange_categories", back_populates="taker_categories")

    def __str__(self):
        return self.name


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    full_description = Column(String, nullable=True)
    address = Column(String, nullable=True)
    schedule = Column(String, nullable=True)
    phone_for_client = Column(String, nullable=True)
    type_company = Column(String, nullable=True)
    inn = Column(String, nullable=True)
    kpp = Column(String, nullable=True)
    ogrn = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    ur_address = Column(String, nullable=True)
    type_discounts = Column(String, nullable=True)
    discount_size = Column(String, nullable=True)
    max_pay_point = Column(JSON, nullable=True)
    cashback = Column(JSON, nullable=True)
    max_pay_point_company = Column(String, nullable=True)
    cashback_company = Column(String, nullable=True)
    visible = Column(Boolean, default=True)
    color = Column(String, nullable=True)
    welcome_balls = Column(String, nullable=True)
    main_photo = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_COMPANIES_MAIN)), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship("Category", lazy='subquery')

    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True)
    city = relationship("City", lazy='subquery')

    # user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    # user = relationship("User")
    another_photo = Column(JSON, nullable=True)

    dop_photo_1 = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_COMPANIES_ANOTHER)), nullable=True)
    dop_photo_2 = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_COMPANIES_ANOTHER)), nullable=True)
    dop_photo_3 = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_COMPANIES_ANOTHER)), nullable=True)
    dop_photo_4 = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_COMPANIES_ANOTHER)), nullable=True)
    dop_photo_5 = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_COMPANIES_ANOTHER)), nullable=True)

    external_links = Column(JSON, nullable=True, default=[])

    link_1 = Column(String, nullable=True)
    link_2 = Column(String, nullable=True)
    link_3 = Column(String, nullable=True)
    link_4 = Column(String, nullable=True)
    link_5 = Column(String, nullable=True)

    news = relationship("News", back_populates="company", lazy="subquery")
    reviews = relationship("Review", back_populates="company", lazy="subquery")
    balls = relationship("Balls", back_populates="company", lazy="subquery")
    coupons = relationship("Coupon", back_populates="company", lazy="subquery")

    clients = relationship('Client', secondary="company_client_link", back_populates="companies")
    tags = relationship("Tag", secondary="company_tag_link", back_populates="companies", lazy="subquery")
    tariffs = relationship("Tariff", secondary="company_tariff_link", back_populates="companies", lazy="subquery")

    holder_company = relationship('Exchange', foreign_keys='Exchange.holder_company_id',
                                  back_populates='holder_company')
    taker_company = relationship('Exchange', foreign_keys='Exchange.taker_company_id', back_populates='taker_company', lazy="subquery")
    exchange_companies = relationship('Exchange', secondary="exchange_companies", back_populates="taker_companies", lazy="subquery")

    reviews_rating = Column(Float, nullable=True)

    delivery = Column(Boolean, default=False)
    time_to_delivery = Column(String, nullable=True)
    products = relationship('Product', back_populates='company', lazy="subquery")
    favorites = relationship('Favorite', back_populates='company', lazy="subquery")
    orders = relationship('Order', back_populates='company', lazy="subquery")
    baskets = relationship('Basket', back_populates='company')

    def __str__(self):
        return str(self.name)


class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    short_description = Column(String)
    description = Column(String)
    link = Column(String)
    visible = Column(Boolean)
    photo = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_NEWS)), nullable=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship('Company', back_populates='news')
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    tags = relationship("Tag", back_populates="news")

    def __str__(self):
        return str(self.name)


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    text_color = Column(String(200))
    background_color = Column(String(200))
    for_company = Column(Boolean)
    for_news = Column(Boolean)
    companies = relationship("Company", secondary="company_tag_link", back_populates="tags")
    news_id = Column(Integer, ForeignKey('news.id'), nullable=True)
    news = relationship('News', back_populates='tags')
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.name)


class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)

    rating = Column(Float)
    advantages = Column(String(1000))
    disadvantages = Column(String(1000))
    comment = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship("Client", back_populates="reviews")

    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship("Company", back_populates="reviews")

    def __str__(self):
        return str(self.rating)


class Balls(Base):
    __tablename__ = 'balls'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=True)
    client = relationship("Client", back_populates="balls")
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    company = relationship("Company", back_populates="balls")
    ball = Column(Integer)
    hide_ball = Column(Integer)
    main_account = Column(Boolean, default=False)
    # transactions = relationship('BallsTransaction', foreign_keys='BallsTransaction.balls_id', back_populates='balls', overlaps="balls_transactions,transactions")
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.ball)


class Coupon(Base):
    __tablename__ = 'coupons'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship("Company", back_populates='coupons', lazy='subquery')
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship("Client", back_populates='coupons')
    price = Column(Integer)
    name = Column(String)
    description = Column(String)
    discount = Column(Float(2))
    link = Column(String)
    date = Column(DateTime())
    color = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.name) or f'None'

    @property
    def company_category(self):
        return self.company.category


class Tariff(Base):
    __tablename__ = 'tariffs'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(200))
    description_two = Column(String(200))
    color = Column(String(50))
    check_list = Column(String(1000))
    check_list_two = Column(String(1000))
    visible = Column(Boolean)
    icon = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_TARIFFS)))
    main = Column(Boolean)
    for_client = Column(Boolean)
    for_company = Column(Boolean)
    clients_tariff_name = Column(String(50))
    cashback = Column(String(50))
    write_of_balls = Column(String(50))
    invite_friends = Column(String(50))
    summ_of_order = Column(String(50))
    summ_witch_friends = Column(String(50))
    reward = Column(String(50))
    companies = relationship("Company", secondary="company_tariff_link", back_populates="tariffs")
    subscribed = relationship('SubscribedTariff', back_populates='tariff', lazy="subquery")
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return self.name


class SubscribedTariff(Base):
    __tablename__ = 'subscribed_tariffs'
    id = Column(Integer, primary_key=True)
    price = Column(Float)
    duration = Column(String(10))
    discount = Column(String(10))
    tariff_id = Column(Integer, ForeignKey('tariffs.id'))
    tariff = relationship('Tariff', back_populates='subscribed', lazy="subquery")
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return self.duration


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship('Client')
    balance = Column(Float)
    up_balance = Column(Float)
    transaction_type = Column(String(50))  # deposit, withdraw, change(from admin)
    status = Column(String(50))  # success, fail, hold
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return f'Баланс: {str(self.balance)}, Апы {str(self.up_balance)}'


class Exchange(Base):
    __tablename__ = 'exchange'
    id = Column(Integer, primary_key=True)

    holder_id = Column(Integer, ForeignKey('clients.id'))
    holder = relationship('Client', foreign_keys=[holder_id], back_populates='given_clients')

    last_holder_id = Column(Integer, ForeignKey('clients.id'))
    last_holder = relationship('Client', foreign_keys=[last_holder_id], back_populates='given_clients')

    taker_id = Column(Integer, ForeignKey('clients.id'), nullable=True)
    taker = relationship('Client', foreign_keys=[taker_id], back_populates='received_clients')

    holder_company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    holder_company = relationship('Company', back_populates='holder_company',
                                  primaryjoin=holder_company_id == Company.id)

    taker_company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    taker_company = relationship('Company', back_populates='taker_company', primaryjoin=taker_company_id == Company.id)

    taker_companies = relationship('Company', secondary=exchange_companies, back_populates='exchange_companies')
    taker_categories = relationship('Category', secondary=exchange_categories, back_populates='exchange_categories')

    counter_deal = Column(Boolean, default=False)  # counteroffer
    type_deal = Column(String(100))  # buy, sell, exchange_sell, exchange
    city_deal = Column(String(100))
    partial_deal = Column(Boolean, default=False)
    give_balls = Column(Integer)
    get_balls = Column(Integer)
    give_saveup = Column(Integer)
    get_saveup = Column(Integer)
    give_cash = Column(Integer)
    get_cash = Column(Integer)
    status = Column(String(100))  # draft, active, completed, hide, canceled
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return f'{self.id}'


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    type = Column(String(200))  # referral, exchange, balls, balance, up_balance, news?,
    icon_type = Column(String(200))
    description_type = Column(String(200))
    icon_notification = Column(String(200))
    title = Column(String(200))
    description = Column(String(500))
    read = Column(Boolean)
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship('Client')
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.title) or f'None'


class MainAccount(Base):
    __tablename__ = 'main_account'
    id = Column(Integer, primary_key=True)
    balance = Column(Float)
    up_balance = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())


class Referral(Base):
    __tablename__ = 'referral'
    id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer, ForeignKey('clients.id'))
    referred_id = Column(Integer, ForeignKey('clients.id'))
    referrer = relationship('Client', foreign_keys=[referrer_id], lazy="subquery")
    referred = relationship('Client', foreign_keys=[referred_id], lazy="subquery")
    level = Column(String(1))
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.level)


class Reward(Base):
    __tablename__ = 'reward'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship('Client', foreign_keys=[client_id], lazy="subquery")
    agent_id = Column(Integer, ForeignKey('clients.id'))
    agent = relationship('Client', foreign_keys=[agent_id], lazy="subquery")
    tariff_id = Column(Integer, ForeignKey('tariffs.id'))
    tariff = relationship('Tariff', foreign_keys=[tariff_id], lazy="subquery")
    duration = Column(Integer)
    amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.amount)


class Story(Base):
    __tablename__ = 'stories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(200))
    photo = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_STORIES_PHOTO)))
    link = Column(String(200))
    visible = Column(Boolean, default=True)
    show_in_search = Column(Boolean, default=False)
    button_name = Column(String(200))
    icon = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_STORIES_ICON)))
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.name)


class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    cashback_coefficient = Column(Float)
    balls_deduction_coefficient = Column(Float)
    discount = Column(Float)  # скидка для клиентов от компаний настраивается из админки
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.id)


class Competition(Base):
    __tablename__ = 'competitions'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    description = Column(String(200))
    photo = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_COMPETITIONS)))
    date_end = Column(Date)
    instant = Column(Boolean, default=False)
    clients = relationship('Client', secondary="competition_clients", back_populates="competitions")
    prizes = relationship('Prize', back_populates="competition", lazy='subquery')
    tickets = relationship('Ticket', back_populates="competition")
    color = Column(String)
    quantity_ticket = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.name)


class Prize(Base):
    __tablename__ = 'prizes'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    description = Column(String(200))
    photo = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_PRIZES)))
    count = Column(Integer)
    competition_id = Column(Integer, ForeignKey('competitions.id'))
    competition = relationship('Competition')
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=True)
    client = relationship("Client", lazy="subquery")
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.name)


class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    color = Column(String)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=True)
    client = relationship("Client", lazy="subquery")
    competition_id = Column(Integer, ForeignKey('competitions.id'))
    competition = relationship('Competition')
    activate = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.name)


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    type = Column(String(200))  # join, buy, invite, login, exchange, tariff,
    short_description = Column(String)
    description = Column(String(1000))
    quantity = Column(String(200))
    photo = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_TASKS)))
    reward_type = Column(String(200))
    reward = Column(Integer)
    date_end = Column(DateTime)
    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship('Company', lazy="subquery")
    status = Column(String(200))
    clients = relationship('Client', secondary="client_tasks", back_populates="tasks")
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.name)


class TransactionCompetition(Base):
    __tablename__ = 'transaction_competitions'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship('Client')
    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship('Task', lazy="subquery")
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.name)


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    place = Column(String(200))
    question = Column(String(1000))
    answer = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.question)


class Franchise(Base):
    __tablename__ = 'franchise'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    phone = Column(String(200))
    comment = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.phone)


class VirtualAccount(Base):
    __tablename__ = 'virtual_account'
    id = Column(Integer, primary_key=True)
    customer_id = Column(String(100))
    status = Column(String(100))  # open, pending, closed
    balance = Column(Float(2))
    up_balance = Column(Float(2))
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship('Client')
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())


class RevocationOfPrivacy(Base):
    __tablename__ = 'revocation_of_privacy'
    id = Column(Integer, primary_key=True)
    phone = Column(String(100))
    comment = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())


class Push(Base):
    __tablename__ = 'push'
    id = Column(Integer, primary_key=True)
    to = Column(String(100))
    title = Column(String(100))
    body = Column(String(100))
    data = Column(JSON)
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship('Client')
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    unit = Column(String, nullable=True)
    description = Column(String, nullable=True)
    weight = Column(String, nullable=True)
    photo = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER_PRODUCTS)), nullable=True)
    quantity = Column(Integer)
    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship('Company')
    category_id = Column(Integer, ForeignKey('products_category.id'))
    category = relationship('ProductsCategory')
    favorites = relationship('Favorite', back_populates='product', lazy="subquery")
    baskets = relationship('Basket', secondary="product_baskets", back_populates="products", lazy="subquery")
    orders = relationship('Order', secondary="product_orders", back_populates="products", lazy="subquery")

    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.name)


class ProductsCategory(Base):
    __tablename__ = 'products_category'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    products = relationship('Product', back_populates='category')
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return str(self.name)


class Favorite(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True)
    is_company = Column(Boolean, default=False)
    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship("Company", back_populates="favorites")
    is_product = Column(Boolean, default=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship("Product", back_populates="favorites")
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship("Client", back_populates="favorites")
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())


class Basket(Base):
    __tablename__ = 'baskets'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship("Client", back_populates="baskets")
    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship("Company", back_populates="baskets")
    products = relationship('Product', secondary="product_baskets", back_populates="baskets", lazy="subquery")
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship("Client", back_populates="orders")
    amount = Column(Float(2))
    promocode = Column(String)
    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship("Company", back_populates="orders")
    products = relationship('Product', secondary="product_orders", back_populates="orders", lazy="subquery")
    write_of_balls = Column(String)
    amount_of_delivery = Column(Float(2))
    accrual_of_balls = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())


class ClientAddress(Base):
    __tablename__ = 'client_addresses'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship("Client", back_populates="addresses")
    address = Column(String)
    oksm_code = Column(String)
    city = Column(String)
    street = Column(String)
    house = Column(String)
    flat = Column(String)
    entrance = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())




# модель жетонов
