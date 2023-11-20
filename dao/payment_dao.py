from datetime import datetime

import pymysql
from pydantic.schema import List

from model.payment import PaymentDetails, GetPayment, UpdatePayment
from config.db import get_connection

cur = get_connection().cursor()


def create_payment(p: PaymentDetails):

    create_payment_stmt = (
        "INSERT INTO `payment` (`name`, `amount_paid`, `payment_date`, `payment_type`, `paid_by`,"
        " `flat_code`)"
        "VALUES (%s, %s, %s, %s, %s, %s)"
    )
    get_payment_id_stmt = (
        "SELECT `payment_id` FROM payment WHERE name = %s "
        "AND payment_date = %s AND paid_by = %s"
    )
    payment_affected_stmt = (
        "INSERT INTO `payment_affected_users` (`payment_id`, `username`, `is_paid`)"
        " VALUES (%s, %s, %s)"
    )

    try:
        # insert into the payments table.
        paid_date = datetime.now()
        cur.execute(
            create_payment_stmt,
            (
                p.payment_name,
                p.paid_amount,
                paid_date,
                p.payment_type,
                p.payee,
                p.flat_code,
            ),
        )

        # Get the payment_id for the newly inserted payment.
        cur.execute(
            get_payment_id_stmt,
            (p.payment_name, paid_date.date(), p.payee),
        )
        payment_id = cur.fetchone()

        # insert into the payment_affected_users table.
        for username in p.affected_flatmates:

            cur.execute(
                payment_affected_stmt,
                (
                    payment_id,
                    username,
                    False,
                ),
            )
        return str(payment_id)
    except pymysql.Error as pe:
        print("Could not create a payment error is " + str(pe))


def get_payment_details_by_flat_code(flat_code: str) -> List[GetPayment]:

    result = []
    get_payment_details_stmt = (
        "SELECT payment_id, flat_code, name, paid_by, amount_paid,"
        " payment_type, payment_date FROM payment where flat_code=%s"
    )
    get_affected_flatmates_for_payment_stmt = (
        "select username, is_paid from payment_affected_users where payment_id=%s"
    )

    try:
        cur.execute(
            get_payment_details_stmt,
            str(flat_code),
        )
        payment_result = cur.fetchall()

        for payment in payment_result:
            cur.execute(
                get_affected_flatmates_for_payment_stmt,
                payment[0],
            )
            affected_users = cur.fetchall()
            affected_users = [(arr[0], arr[1]) for arr in affected_users]
            ret = GetPayment(
                payment_id=payment[0],
                flat_code=payment[1],
                payment_name=payment[2],
                payee=payment[3],
                paid_amount=payment[4],
                payment_type=payment[5],
                payment_date=str(payment[6]),
                affected_flatmates=affected_users,
            )
            result.append(ret)
    except pymysql.Error as pe:

        print("Could not retrieve payment details " + str(pe))

    return result


def get_payment_details_by_username(username: str) -> List[GetPayment]:

    result = []
    get_payment_details_stmt = (
        "SELECT payment_id, flat_code, name, paid_by, amount_paid,"
        " payment_type, payment_date FROM payment where paid_by=%s"
    )
    get_affected_flatmates_for_payment_stmt = (
        "select username, is_paid from payment_affected_users where payment_id=%s"
    )

    try:
        cur.execute(
            get_payment_details_stmt,
            str(username),
        )
        payment_result = cur.fetchall()

        for payment in payment_result:
            cur.execute(
                get_affected_flatmates_for_payment_stmt,
                payment[0],
            )
            affected_users = cur.fetchall()
            affected_users = [(arr[0], arr[1]) for arr in affected_users]
            ret = GetPayment(
                payment_id=payment[0],
                flat_code=payment[1],
                payment_name=payment[2],
                payee=payment[3],
                paid_amount=payment[4],
                payment_type=payment[5],
                payment_date=str(payment[6]),
                affected_flatmates=affected_users,
            )
            result.append(ret)
    except pymysql.Error as pe:

        print("Could not retrieve payment details " + str(pe))

    return result


def get_payment_details_involve_username(username: str) -> List[GetPayment]:

    result = []
    get_payment_details_stmt = (
        "SELECT payment_id, flat_code, name, paid_by, amount_paid,"
        " payment_type, payment_date FROM payment where payment_id=%s"
    )
    get_affected_flatmates_for_payment_stmt = (
        "select payment_id from payment_affected_users where username=%s"
    )

    try:
        cur.execute(
            get_affected_flatmates_for_payment_stmt,
            str(username),
        )
        payment_result = cur.fetchall()

        for payment in payment_result:
            cur.execute(
                get_payment_details_stmt,
                payment[0],
            )
            payment_det = cur.fetchone()
            print(payment_det)

            ret = GetPayment(
                payment_id=payment_det[0],
                flat_code=payment_det[1],
                payment_name=payment_det[2],
                payee=payment_det[3],
                paid_amount=payment_det[4],
                payment_type=payment_det[5],
                payment_date=str(payment_det[6]),
                affected_flatmates=[],
            )
            result.append(ret)
    except pymysql.Error as pe:

        print("Could not retrieve payment details " + str(pe))

    return result


def update_payment_by_user(p_id: int, username: str):

    update_payment_stmt = ("UPDATE payment_affected_users "
                           "SET is_paid=1 "
                           "where payment_id=%s and username=%s")

    try:
        cur.execute(
            update_payment_stmt,
            (str(p_id), username),
        )
        return True
    except pymysql.Error as pe:

        print("Could not retrieve payment details " + str(pe))


def update_payment_details(payment_details: UpdatePayment):

    update_payment_stmt = ("UPDATE payment "
                           "SET name=%s, paid_by=%s, payment_date=%s, amount_paid=%s,"
                           " payment_type=%s "
                           "where payment_id=%s")

    update_affected_user_stmt = (
        "INSERT INTO `payment_affected_users` (`payment_id`, `username`, `is_paid`)"
        " VALUES (%s, %s, %s)"
    )

    try:
        cur.execute(
            update_payment_stmt,
            (payment_details.payment_name, payment_details.payee, payment_details.payment_date,
             payment_details.paid_amount, payment_details.payment_type, payment_details.payment_id),
        )
        for username in payment_details.affected_flatmates:

            cur.execute(
                update_affected_user_stmt,
                (
                    payment_details.payment_id,
                    username,
                    False,
                ),
            )

        return True
    except pymysql.Error as pe:

        print("Could not retrieve payment details " + str(pe))


def delete_payment(p_id: int):

    delete_payment_stmt = "delete from payment where payment_id=%s"
    delete_payment_affected_users = (
        "delete from payment_affected_users where payment_id=%s"
    )
    try:
        cur.execute(
            delete_payment_stmt,
            str(p_id),
        )
        cur.execute(
            delete_payment_affected_users,
            p_id,
        )
        return True
    except pymysql.Error as pe:

        print("Could not create a payment error is " + str(pe))
