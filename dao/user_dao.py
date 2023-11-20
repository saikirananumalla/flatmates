from model import user as us
import hashlib

from config.db import get_connection

cur = get_connection().cursor()


def get_user_by_user_name(username: str):

    get_by_username_stmt = (
        "SELECT username, email_id, phone FROM user WHERE username=%s"
    )
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


def get_user_by_email(email_id: str):

    get_user_by_email_stmt = (
        "SELECT username, email_id, phone, password FROM user WHERE user.email_id=%s"
    )
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


def create_user(user: us.UserWithPassword):
    
    # Hash the password using SHA-256
    hashed_password = hashlib.sha256(user.password.encode('utf-8')).hexdigest()

    create_user_stmt = (
        "INSERT INTO `user` (`username`, `email_id`, `phone`, `password`)"
        " VALUES (%s, %s, %s, %s)"
    )
    cur.execute(
        create_user_stmt, (user.username, user.email_id, user.phone, hashed_password)
    )
    return get_user_by_user_name(username=user.username)


def delete_user_by_user_name(username: str):

    delete_by_username_stmt = "DELETE FROM user WHERE user.username=%s"
    cur.execute(delete_by_username_stmt, username)
    return cur.rowcount > 0
    
