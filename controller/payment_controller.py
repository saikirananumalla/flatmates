from pydantic.schema import List

from model import payment as pm
from dao import payment_dao
from fastapi import APIRouter, HTTPException

from model.payment import GetPayment, UpdatePayment

payment_router = APIRouter()


@payment_router.post("/payment/", response_model=pm.PaymentDetailsWithId, tags=["payments"])
def create_payment(payment_details: pm.PaymentDetails):
    try:
        payment_result = payment_dao.create_payment(p=payment_details)
        return payment_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@payment_router.get("/payment_by_flat", response_model=List[GetPayment], tags=["payments"])
def get_payment_by_flat(flat_code: str):
    try:
        payments_result = payment_dao.get_payment_details_by_flat_code(flat_code=flat_code)
        return payments_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@payment_router.get("/payment_by_username", response_model=List[GetPayment], tags=["payments"])
def get_payment_by_username(username: str):
    try:
        payments_result = payment_dao.get_payment_details_by_username(username=username)
        return payments_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))



@payment_router.get("/payments_involve_username", response_model=List[GetPayment], tags=["payments"])
def get_payment_involve_username(username: str):
    try:
        payments_result = payment_dao.get_payment_details_involve_username(username=username)
        return payments_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@payment_router.patch("/update_payment_by_user", response_model=str, tags=["payments"])
def update_payment_by_user(payment_id: int, username: str):
    try:
        payments_result = payment_dao.update_payment_by_user(
            p_id=payment_id, username=username
        )
        return payments_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@payment_router.patch("/update_payment_details", response_model=UpdatePayment, tags=["payments"])
def update_payment_details(payment_details: UpdatePayment):
    try:

        update_payments_result = payment_dao.update_payment_details(
            payment_details
        )
        return update_payments_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@payment_router.delete("/delete_payment_by_id", response_model=str, tags=["payments"])
def delete_payment_by_id(payment_id: int):
    try:
        payments_result = payment_dao.delete_payment(p_id=payment_id)
        return payments_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
