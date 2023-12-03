from pydantic import BaseModel
from pydantic.schema import List, Tuple
from typing import Optional


class UpdatePayment(BaseModel):

    payment_name: str
    payee: str
    payment_date: str
    affected_flatmates: Optional[List[str]]
    paid_amount: float
    payment_type: str
    payment_id: int = None


class PaymentDetails(BaseModel):
    payment_name: str
    payee: str
    payment_date: str
    affected_flatmates: Optional[List[str]]
    paid_amount: float
    payment_type: str
    flat_code: str


class PaymentDetailsWithOutFlatCode(BaseModel):
    payment_name: str
    payee: str
    payment_date: str
    affected_flatmates: Optional[List[str]]
    paid_amount: float
    payment_type: str


class PaymentDetailsWithId(PaymentDetails):
    
    payment_id: str


class GetPayment(BaseModel):

    payment_id: int
    flat_code: str
    payment_name: str
    payee: str
    paid_amount: float
    payment_type: str
    payment_date: str
    affected_flatmates: Optional[List[Tuple[str, str]]]


class UserMoney(BaseModel):

    user: str
    money: float


class MoneyTotal(BaseModel):

    total_money: float
    individual_money: Optional[List[UserMoney]]
