from pydantic import BaseModel
from pydantic.schema import List, Tuple


class UpdatePayment(BaseModel):

    payment_name: str
    payee: str
    payment_date: str
    affected_flatmates: List[str]
    paid_amount: float
    payment_type: str
    payment_id: int = None


class PaymentDetails(UpdatePayment):

    flat_code: str


class GetPayment(BaseModel):

    payment_id: int
    flat_code: str
    payment_name: str
    payee: str
    paid_amount: float
    payment_type: str
    payment_date: str
    affected_flatmates: List[Tuple[str, str]]
