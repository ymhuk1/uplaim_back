from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union, ForwardRef
from pydantic import BaseModel, Field


class SClientId(BaseModel):
    id: int


class SendPhoneNumberIn(BaseModel):
    phone: str
    device: dict
    referral_code: Optional[str] = None
    push_token: Optional[str] = None


class SendPhoneNumberOut(BaseModel):
    message: str
    token: str
    new_user: bool


class VerifySMSDataIn(BaseModel):
    sms_code: int
    token: str


class VerifySMSDataOut(BaseModel):
    message: str


class PaymentMethodRequest(BaseModel):
    method_type: Optional[str] = None
    card_number: Optional[str] = None
    expiry_data: Optional[str] = None
    cvv: Optional[str] = None
    sbp_phone: Optional[str] = None
    bik: Optional[str] = None
    visible: Optional[bool] = None
    is_primary: Optional[bool] = None


class PaymentMethodResponse(BaseModel):
    id: Optional[int] = None
    method_type: Optional[str] = None
    card_number: Optional[str] = None
    expiry_data: Optional[str] = None
    cvv: Optional[str] = None
    sbp_phone: Optional[str] = None
    bik: Optional[str] = None
    visible: Optional[bool] = None
    is_primary: Optional[bool] = None


class ClientEditDataIn(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    city: Optional[str] = None
    payment_methods: Optional[PaymentMethodRequest] = None


class ClientResponse(BaseModel):
    id: int
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    city: Optional[str] = None
    payment_methods: Optional[List[PaymentMethodResponse]] = []

    # class Config:
    #     orm_mode = True


class PasswordData(BaseModel):
    password: str
    token: str


class SPasswordData(BaseModel):
    message: Optional[str] = None


class LoginData(BaseModel):
    password: str
    token: str


class SLoginData(BaseModel):
    message: Optional[str] = None


class CategoryModel(BaseModel):
    id: int
    name: str


class PhotoModel(BaseModel):
    id: int
    filename: str


class ReviewModel(BaseModel):
    id: Optional[int] = None
    rating: Optional[float] = None


class NewsModel(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    photo: Optional[str] = None
    short_description: Optional[str] = None


class CouponModel(BaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    company_id: Optional[int] = None
    # company:
    price: Optional[int] = None
    name: Optional[str] = None
    discount: Optional[float] = None
    link: Optional[str] = None
    date: Optional[datetime] = None
    color: Optional[str] = None


class CityModel(BaseModel):
    id: int
    name: str


class BallsModel(BaseModel):
    id: int
    client_id: Optional[int] = None
    company_id: Optional[int] = None
    ball: Optional[int] = None
    hide_ball: Optional[int] = None


class TariffModel(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    description_two: Optional[str] = None
    color: Optional[str] = None
    check_list: Optional[str] = None
    check_list_two: Optional[str] = None
    icon: Optional[str] = None
    clients_tariff_name: Optional[str] = None
    cashback: Optional[str] = None
    write_of_balls: Optional[str] = None
    summ_of_order: Optional[str] = None
    summ_witch_friends: Optional[str] = None
    # reward: Optional[str] = None
    # subscribed: Optional[str] = None


class TagModel(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    text_color: Optional[str] = None
    background_color: Optional[str] = None


class CategoryCompanies(BaseModel):
    category_id: int


class TransactionModel(BaseModel):
    id: int
    balance: Optional[float] = None
    up_balance: Optional[float] = None
    transaction_type: Optional[str] = None
    status: Optional[str] = None
    created_on: datetime | None
    updated_on: datetime | None


class CompanyModel(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    full_description: Optional[str] = None
    address: Optional[str] = None
    schedule: Optional[str] = None
    phone_for_client: Optional[str] = None
    type_company: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    ogrn: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    ur_address: Optional[str] = None
    type_discounts: Optional[str] = None
    discount_size: Optional[str] = None
    max_pay_point: Optional[dict] = {}
    cashback: Optional[dict] = {}
    visible: Optional[bool] = None
    color: Optional[str] = None
    welcome_balls: Optional[str] = None
    main_photo: Optional[str] = None
    city: CityModel | None
    city_id: Optional[int] = None
    category: CategoryModel
    category_id: Optional[int] = None
    another_photo: Optional[list] = []
    external_links: Optional[list] = []
    reviews: List[ReviewModel] = []
    news: List[NewsModel] = []
    coupons: List[CouponModel] = []
    reviews_rating: Optional[float] = None
    tariffs: Optional[List[TariffModel]] = []
    tags: Optional[List[TagModel]] = []


class CompanyModelOne(BaseModel):
    company_id: int
    token: Optional[str] = None


class AssociateCompany(BaseModel):
    client_id: int
    company_id: int


class ReviewCreate(BaseModel):
    client_id: int
    company_id: int
    rating: Optional[int] = None
    advantages: Optional[str] = None
    disadvantages: Optional[str] = None
    comment: Optional[str] = None


class ReviewCreateMessage(BaseModel):
    message: Optional[str] = None
    status: Optional[str] = None


class Notification_schema(BaseModel):
    id: int
    type: Optional[str] = None
    icon_type: Optional[str] = None
    description_type: Optional[str] = None
    icon_notification: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    read: Optional[bool] = None
    created_at: datetime | None


class Referrals(BaseModel):
    id: int
    referred_id: int
    level: Optional[str] = None


class ClientIn(BaseModel):
    token: str


class ClientOut(BaseModel):
    id: int
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[int] = None
    email: Optional[str] = None
    referral_link: Optional[str] = None
    reviews: List[ReviewModel] = []
    companies: List[CompanyModel] = []
    balls: List[BallsModel] = []
    city: CityModel | None
    city_id: Optional[int] = None
    tariff_id: Optional[int] = None
    tariff: TariffModel | None
    tariff_start: datetime | None
    tariff_day: Optional[str] = None
    tariff_end: datetime | None
    transactions: List[TransactionModel] = []
    notify: List[Notification_schema] = []
    referrals: List[Referrals] = []
    # given_clients: Optional[str] = None
    # received_clients: Optional[str] = None
    # competitions: Optional[str] = None


class MessageSearchCompanies(BaseModel):
    message: str


class StoryModel(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    photo: Optional[str] = None
    link: Optional[str] = None
    icon: Optional[str] = None
    button_name: Optional[str] = None
    created_at: datetime | None


class GetSubscribedTariffs(BaseModel):
    tariff_id: int


class AssociateTariff(BaseModel):
    client_id: int
    tariff_id: int
    subscribed_tariff_id: int


class AssociateTariffOut(BaseModel):
    message: Optional[str] = None


class ExchangeMyBallsIn(BaseModel):
    category: Optional[str] = None
    city: Optional[str] = None


class ExchangeTakerCompanies(BaseModel):
    id: int


class ExchangeTakerCategories(BaseModel):
    id: int


class ExchangeCreateIn(BaseModel):
    holder_id: int
    type_deal: str
    status: Optional[str] = None
    holder_company_id: Optional[int] = None
    taker_companies: Optional[list] = None
    taker_categories: Optional[list] = None
    give_balls: Optional[int] = None
    get_balls: Optional[int] = None
    give_saveup: Optional[int] = None
    get_saveup: Optional[int] = None
    give_cash: Optional[int] = None
    get_cash: Optional[int] = None
    last_holder_id: Optional[int] = None
    counter_deal: Optional[bool] = None
    partial_deal: Optional[bool] = None
    city_deal: Optional[str] = None


class UpdateExchange(BaseModel):
    taker_id: Optional[int] = None
    holder_company_id: Optional[int] = None
    counter_deal: Optional[bool] = None
    partial_deal: Optional[bool] = None
    type_deal: Optional[str] = None
    city_deal: Optional[str] = None
    give_balls: Optional[int] = None
    get_balls: Optional[int] = None
    give_saveup: Optional[int] = None
    get_saveup: Optional[int] = None
    give_cash: Optional[int] = None
    get_cash: Optional[int] = None
    status: Optional[str] = None
    taker_companies: Optional[list] = None
    taker_categories: Optional[list] = None


class NotifyData(BaseModel):
    client_id: int
    is_read: Optional[bool] = None
    date: Optional[datetime] = None
    type_notify: Optional[str] = None


class FranchiseData(BaseModel):
    name: str
    phone: str
