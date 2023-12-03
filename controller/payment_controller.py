from pydantic.schema import List

from config.oauth import get_current_user
from model import payment as pm, user
from dao import payment_dao
from fastapi import APIRouter, HTTPException, Depends

from model.payment import GetPayment, UpdatePayment

payment_router = APIRouter()


@payment_router.post("/payment/", response_model=pm.PaymentDetailsWithId, tags=["payments"])
def create_payment(payment_details: pm.PaymentDetails,
                   current_user: user.AuthUser = Depends(get_current_user)):
    try:
        if payment_details.flat_code != current_user.flat_code:
            raise HTTPException(status_code=401, detail="User not authorised to create a payment")
        payment_result = payment_dao.create_payment(p=payment_details)
        return payment_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@payment_router.get("/payment_by_flat", response_model=List[GetPayment], tags=["payments"])
def get_payment_by_flat(current_user: user.AuthUser = Depends(get_current_user)):
    try:
        payments_result = (payment_dao.
                           get_payment_details_by_flat_code(flat_code=current_user.flat_code))
        return payments_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@payment_router.get("/payment_by_username", response_model=List[GetPayment], tags=["payments"])
def get_payment_by_username(current_user: user.AuthUser = Depends(get_current_user)):
    try:
        payments_result = (
            payment_dao.get_payment_details_by_username(username=current_user.username))
        return payments_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@payment_router.get("/payments_involve_username",
                    response_model=List[GetPayment], tags=["payments"])
def get_payment_involve_username(current_user: user.AuthUser = Depends(get_current_user)):
    try:
        payments_result = (
            payment_dao.get_payment_details_involve_username(username=current_user.username))
        return payments_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@payment_router.patch("/mark_payment_as_done", response_model=str, tags=["payments"])
def mark_payment_as_done(payment_id: int, paid_status: bool,
                         current_user: user.AuthUser = Depends(get_current_user)):
    try:
        payments_result = payment_dao.update_payment_by_user(
            p_id=payment_id, username=current_user.username, paid_status=paid_status)
        return payments_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@payment_router.patch("/update_payment_details", response_model=UpdatePayment,
                      tags=["payments"])
def update_payment_details(payment_details: UpdatePayment,
                           current_user: user.AuthUser = Depends(get_current_user)):
    try:
        if payment_details.payee != current_user.username:
            raise HTTPException(status_code=401, detail="User not authorised to update a payment")
        update_payments_result = payment_dao.update_payment_details(
            payment_details)
        return update_payments_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@payment_router.delete("/delete_payment_by_id", response_model=str, tags=["payments"])
def delete_payment_by_id(payment_id: int, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        payments_result = payment_dao.delete_payment(p_id=payment_id,
                                                     flat_code_user=current_user.flat_code)
        return payments_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
