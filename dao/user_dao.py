from model import user as us
import hashlib
from pymysql import MySQLError

from config.db import get_connection


def get_user_by_user_name(username: str):
    try:
        get_by_username_stmt = (
            "SELECT username, email_id, phone FROM user WHERE username=%s"
        )
        with get_connection().cursor() as cur:
            cur.execute(get_by_username_stmt, (username,))
            result = cur.fetchone()

            if not result:
                return None

            user_model = us.User(
                        username=result[0],
                        email_id=result[1],
                        phone=result[2]
                    )
            return user_model
    except MySQLError as e:
        raise ValueError(f"Error getting user: pls check your inputs")


def get(username: str):
    try:
        get_by_username_stmt = (
            "SELECT * FROM user WHERE username=%s"
        )
        with get_connection().cursor() as cur:
            cur.execute(get_by_username_stmt, (username,))
            result = cur.fetchone()

            if not result:
                return None

            user_model = us.UserWithPassword(
                        username=result[0],
                        email_id=result[1],
                        phone=result[2],
                        password=result[3]
                    )
            return user_model
    except MySQLError as e:
        raise ValueError(f"Error getting user: pls check your inputs")


def get_user_by_email(email_id: str):
    try:
        get_user_by_email_stmt = (
            "SELECT username, email_id, phone, password FROM user WHERE user.email_id=%s"
        )
        with get_connection().cursor() as cur:
            cur.execute(get_user_by_email_stmt, email_id)
            result = cur.fetchone()
            if not result:
                return None

            user_model = us.User(
                        username=result[0],
                        email_id=result[1],
                        phone=result[2]
                    )
            return user_model
    except MySQLError as e:
        raise ValueError(f"Error getting user: pls check your inputs")


def create_user(user: us.UserWithPassword):
    try:
        # Hash the password using SHA-256
        hashed_password = hashlib.sha256(user.password.encode('utf-8')).hexdigest()

        create_user_stmt = (
            "INSERT INTO `user` (`username`, `email_id`, `phone`, `password`)"
            " VALUES (%s, %s, %s, %s)"
        )
        with get_connection().cursor() as cur:
            cur.execute(
                create_user_stmt, (user.username, user.email_id, user.phone, hashed_password)
            )
            return get_user_by_user_name(username=user.username)
    except MySQLError as e:
        raise ValueError(f"Error creating user: pls check your inputs")


def delete_user_by_user_name(username: str):
    try:
        delete_by_username_stmt = "DELETE FROM user WHERE user.username=%s"
        with get_connection().cursor() as cur:
            cur.execute(delete_by_username_stmt, username)
            return cur.rowcount > 0
    except MySQLError as e:
        raise ValueError(f"Error deleting user: pls check your inputs")


def update_user_profile(user_details: us.UpdateProfile, username: str) -> us.User:

    update_user_profile_stmt = (
        "UPDATE user SET email_id=%s, phone=%s, password=%s WHERE username=%s"
    )
    get_email_stmt = (
        "SELECT * FROM user WHERE email_id=%s and username!=%s"
    )
    try:
        with get_connection().cursor() as cur:
            cur.execute(get_email_stmt, (user_details.email_id, username))

            if cur.rowcount > 0:
                raise ValueError(f"Email ID already exists for " + user_details.email_id)

            hashed_password = hashlib.sha256(user_details.password.encode('utf-8')).hexdigest()
            cur.execute(update_user_profile_stmt, (user_details.email_id, user_details.phone,
                                                   hashed_password, username),)
            return get_user_by_user_name(username=username)
    except MySQLError as e:
        raise ValueError(f"Error updating user: Check your inputs" + str(e))
