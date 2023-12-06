import pymysql
from pydantic.schema import List
from pymysql import MySQLError

from config.db import get_connection
from model.payment import PaymentDetails, GetPayment, UpdatePayment, PaymentDetailsWithId, MoneyTotal, UserMoney
from model.payment import (
    PaymentDetails,
    GetPayment,
    UpdatePayment,
    PaymentDetailsWithId,
    UserMoney,
    MoneyTotal,
)


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
        with get_connection().cursor() as cur:
            cur.execute(
                create_payment_stmt,
                (
                    p.payment_name,
                    p.paid_amount,
                    p.payment_date,
                    p.payment_type,
                    p.payee,
                    p.flat_code,
                ),
            )

            # Get the payment_id for the newly inserted payment.
            cur.execute(
                get_payment_id_stmt,
                (p.payment_name, p.payment_date, p.payee),
            )
            payment_id = cur.fetchone()
        
            try:

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
            except MySQLError:
                delete_payment(payment_id[0], p.flat_code)
                raise ValueError(f"Error creating payment: pls check affected flatmates")
            return PaymentDetailsWithId(
                payment_name=p.payment_name,
                payee=p.payee,
                payment_date=p.payment_date,
                affected_flatmates=p.affected_flatmates,
                paid_amount=p.paid_amount,
                payment_type=p.payment_type,
                flat_code=p.flat_code,
                payment_id=payment_id[0])
        
    except pymysql.Error as pe:
        raise ValueError("Could not create a payment " + "pls check your inputs" + str(pe))


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
        with get_connection().cursor() as cur:
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

        raise ValueError("Could not retrieve payment details: " + str(pe))

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
        with get_connection().cursor() as cur:
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
    except pymysql.Error:

        raise ValueError("Could not retrieve payment details pls check your inputs")

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
    get_affected_flatmates_for_payment_stmt_by_id = (
        "select username, is_paid from payment_affected_users where payment_id=%s"
    )

    try:
        with get_connection().cursor() as cur:
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
                
                cur.execute(
                    get_affected_flatmates_for_payment_stmt_by_id,
                    payment_det[0],
                )
                affected_users = cur.fetchall()
                affected_users = [(arr[0], arr[1]) for arr in affected_users]

                ret = GetPayment(
                    payment_id=payment_det[0],
                    flat_code=payment_det[1],
                    payment_name=payment_det[2],
                    payee=payment_det[3],
                    paid_amount=payment_det[4],
                    payment_type=payment_det[5],
                    payment_date=str(payment_det[6]),
                    affected_flatmates=affected_users,
                )
                result.append(ret)
    except pymysql.Error:

        raise ValueError("Could not retrieve payment details pls check your inputs")

    return result


def update_payment_by_user(p_id: int, username: str, paid_status: bool):
    
    paid = 0
    if paid_status:
        paid = 1

    update_payment_stmt = ("UPDATE payment_affected_users "
                           "SET is_paid=%s "
                           "where payment_id=%s and username=%s")

    try:
        with get_connection().cursor() as cur:
            cur.execute(
                update_payment_stmt,
                (str(paid), str(p_id), username),
            )
            return cur.rowcount > 0
    except pymysql.Error:

        raise ValueError("Could not retrieve payment details pls check your inputs")


def update_payment_details(payment_details: UpdatePayment):

    update_payment_stmt = ("UPDATE payment "
                           "SET name=%s, paid_by=%s, payment_date=%s, amount_paid=%s,"
                           " payment_type=%s "
                           "where payment_id=%s")

    drop_affected_user_stmt = "delete from payment_affected_users where payment_id=%s"
    
    update_affected_user_stmt = (
        "INSERT INTO `payment_affected_users` (`payment_id`, `username`, `is_paid`)"
        " VALUES (%s, %s, %s)"
    )

    try:
        with get_connection().cursor() as cur:
            cur.execute(
                update_payment_stmt,
                (payment_details.payment_name, payment_details.payee, payment_details.payment_date,
                payment_details.paid_amount, payment_details.payment_type, payment_details.payment_id),
            )
            
            cur.execute(drop_affected_user_stmt, payment_details.payment_id)
            
            for username in payment_details.affected_flatmates:

                cur.execute(
                    update_affected_user_stmt,
                    (
                        payment_details.payment_id,
                        username,
                        False,
                    ),
                )

            return payment_details
    except pymysql.Error:

        raise ValueError("Could not retrieve payment details pls check your inputs")


def delete_payment(p_id: int, flat_code_user: str):

    delete_payment_stmt = "delete from payment where payment_id=%s"
    delete_payment_affected_users = (
        "delete from payment_affected_users where payment_id=%s"
    )
    try:

        check_user_in_flat(flat_code_user, p_id)
        with get_connection().cursor() as cur:

            cur.execute(
                delete_payment_stmt,
                str(p_id),
            )
            cur.execute(
                delete_payment_affected_users,
                p_id,
            )
            return cur.rowcount > 0
    except pymysql.Error:

        raise ValueError("Could not delete a payment error pls check your inputs")


def check_user_in_flat(flat_code_user, p_id):
    with get_connection().cursor() as cur:
        cur.execute("select flat_code from payment where payment_id = %s",
                    p_id)
        res = cur.fetchone()
        if res is None:
            raise ValueError("Invalid Payment ID")
        if res[0] != flat_code_user:
            raise ValueError("User not in the flat")


def get_money_owed(username: str):

    try:

        total_money = 0
        result_payments = get_payment_details_by_username(username=username)
        user_list = []
        user_dict_temp = {}
        for payment in result_payments:

            num_unpaid_users = 0
            number_of_users = len(payment.affected_flatmates)
            to_be_paid = payment.paid_amount / number_of_users
            for user in payment.affected_flatmates:

                if user[1] == "1":
                    continue
                else:
                    num_unpaid_users = num_unpaid_users + 1
                    if user[0] in user_dict_temp.keys():
                        user_dict_temp[user[0]] = user_dict_temp[user[0]] + to_be_paid
                    else:
                        user_dict_temp[user[0]] = to_be_paid

            total_money = total_money + (payment.paid_amount / number_of_users) * num_unpaid_users

        for user_money in user_dict_temp.items():

            user_list.append(UserMoney(user=user_money[0], money=user_money[1]))

        return MoneyTotal(total_money=total_money, individual_money=user_list)

    except pymysql.Error as pe:
        raise ValueError("Could not get money owed: " + str(pe))


def get_money_owe(username):

    money_owe = {}
    total = 0

    try:
        payments = get_payment_details_involve_username(username)
        for payment in payments:
            for tup in payment.affected_flatmates:
                roommate = tup[0]
                has_paid = tup[1]
                if roommate == username and has_paid == "0":
                    amount = payment.paid_amount / len(payment.affected_flatmates)
                    total = total + amount
                    money_owe.setdefault(payment.payee, 0)
                    money_owe[payment.payee] += amount


        user_list = []

        for key in money_owe.items():
            user_list.append(UserMoney(user=key[0], money=key[1]))

        return MoneyTotal(total_money=total, individual_money= user_list)


    except Exception as e:
        raise ValueError("Error fetching money this user owes" + str(e))
