from datetime import datetime

import pymysql

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


def get_payment_details_by_id(p_id: int) -> GetPayment:

    # Initializing the results for the object
    result = None
    affected_users = None

    get_payment_details_stmt = (
        "SELECT payment_id, flat_code, name, paid_by, amount_paid,"
        " payment_type, payment_date FROM payment where payment_id=%s"
    )
    get_affected_flatmates_for_payment_stmt = (
        "select username, is_paid from payment_affected_users where payment_id=%s"
    )

    try:
        cur.execute(
            get_payment_details_stmt,
            str(p_id),
        )
        result = cur.fetchone()
        cur.execute(
            get_affected_flatmates_for_payment_stmt,
            p_id,
        )
        affected_users = cur.fetchall()
        affected_users = [(arr[0], arr[1]) for arr in affected_users]
    except pymysql.Error as pe:

        print("Could not retrieve payment details " + str(pe))

    ret = GetPayment(
        payment_id=result[0],
        flat_code=result[1],
        payment_name=result[2],
        payee=result[3],
        paid_amount=result[4],
        payment_type=result[5],
        payment_date=str(result[6]),
        affected_flatmates=affected_users,
    )
    return ret


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
