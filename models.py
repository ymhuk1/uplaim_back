from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Table, Float, JSON
from sqlalchemy.orm import declarative_base, relationship
from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import FileType

from config import STATIC_FOLDER


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
    Column('client_id', Integer, ForeignKey('clients.id'), primary_key=True)
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

    notify = relationship('Notification', back_populates='client', lazy="subquery")
    referrals = relationship('Referral', back_populates='referrer', foreign_keys='Referral.referrer_id', lazy="subquery")

    given_clients = relationship('Exchange', foreign_keys='Exchange.holder_id', back_populates='holder', lazy="subquery")
    received_clients = relationship('Exchange', foreign_keys='Exchange.taker_id', back_populates='taker', lazy="subquery")

    competitions = relationship('Competition', secondary="competition_clients", back_populates="clients", lazy="subquery")
    tasks = relationship('Task', secondary="client_tasks", back_populates="clients", lazy="subquery")

    def __str__(self):
        return str(self.phone)


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    icon = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER + '/img' + '/category')), nullable=True)
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
    visible = Column(Boolean, default=True)
    color = Column(String, nullable=True)
    welcome_balls = Column(String, nullable=True)
    main_photo = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER + '/img' + '/company' + '/main_photo')), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship("Category", lazy='subquery')

    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True)
    city = relationship("City", lazy='subquery')

    # user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    # user = relationship("User")
    another_photo = Column(JSON, nullable=True)

    dop_photo_1 = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER + '/img' + '/company' + '/another_photo')), nullable=True)
    dop_photo_2 = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER + '/img' + '/company' + '/another_photo')), nullable=True)
    dop_photo_3 = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER + '/img' + '/company' + '/another_photo')), nullable=True)
    dop_photo_4 = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER + '/img' + '/company' + '/another_photo')), nullable=True)
    dop_photo_5 = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER + '/img' + '/company' + '/another_photo')), nullable=True)

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
    taker_company = relationship('Exchange', foreign_keys='Exchange.taker_company_id', back_populates='taker_company')
    exchange_companies = relationship('Exchange', secondary="exchange_companies", back_populates="taker_companies")

    reviews_rating = Column(Float, nullable=True)

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
    photo = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER + '/img' + '/news')), nullable=True)
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
        return self.name

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
    icon = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER + '/img' + '/tariff')))
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
    subscribed = relationship('SubscribedTariff', back_populates='tariff')
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
    tariff = relationship('Tariff', back_populates='subscribed')
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
        return f'Баланс: {self.balance}, Апы {self.up_balance}'


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


class Story(Base):
    __tablename__ = 'stories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(200))
    photo = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER + '/img' + '/story' + '/photo')))
    link = Column(String(200))
    visible = Column(Boolean)
    show_in_search = Column(Boolean)
    icon = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER + '/img' + '/story' + '/icon')))
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())


class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    cashback_coefficient = Column(Float)
    balls_deduction_coefficient = Column(Float)
    discount = Column(Float)  # скидка для клиентов от компаний настраивается из админки
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())


class Competition(Base):
    __tablename__ = 'competitions'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    description = Column(String(200))
    photo = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER + '/img' + '/competition')))
    date_end = Column(DateTime)
    instant = Column(Boolean, default=False)
    clients = relationship('Client', secondary="competition_clients", back_populates="competitions")
    prizes = relationship('Prize', back_populates="competition")
    tickets = relationship('Ticket', back_populates="competition")
    color = Column(String)
    quantity_ticket = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return self.name


class Prize(Base):
    __tablename__ = 'prizes'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    description = Column(String(200))
    photo = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER + '/img' + '/prize')))
    count = Column(Integer)
    competition_id = Column(Integer, ForeignKey('competitions.id'))
    competition = relationship('Competition')
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=True)
    client = relationship("Client", lazy="subquery")
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __str__(self):
        return self.name


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


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    short_description = Column(String)
    description = Column(String(1000))
    photo = Column(FileType(storage=FileSystemStorage(path=STATIC_FOLDER + '/img' + '/task')))
    reward_type = Column(String(200))
    reward = Column(String(200))
    date_end = Column(DateTime)
    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship('Company', lazy="subquery")
    status = Column(String(200))
    clients = relationship('Client', secondary="client_tasks", back_populates="tasks")
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())


class TransactionCompetition(Base):
    __tablename__ = 'transaction_competitions'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship('Task', lazy="subquery")
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    place = Column(String(200))
    question = Column(String(1000))
    answer = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())



# модель жетонов
