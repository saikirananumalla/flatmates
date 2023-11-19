from model import user as us

from config.db import get_connection

cur = get_connection().cursor()


def get_user_by_user_name(user_name: str):

    get_by_username_stmt = (
        "SELECT username, email_id, phone, password FROM user WHERE user.username=%s"
    )
    cur.execute(get_by_username_stmt, user_name)
    result = cur.fetchall()

    if len(result) == 0:
        return None

    result_dict = {
        "user_name": result[0][0],
        "email_id": result[0][1],
        "phone": result[0][2],
        "password": result[0][3],
    }
    return result_dict


def get_users_by_email(email_id: str):

    get_user_by_email_stmt = (
        "SELECT username, email_id, phone, password FROM user WHERE user.email_id=%s"
    )
    cur.execute(get_user_by_email_stmt, email_id)
    result = cur.fetchall()
    result_list = []
    for i in range(len(result)):
        result_dict_temp = {
            "user_name": result[i][0],
            "email_id": result[i][1],
            "phone": result[i][2],
            "password": result[i][3],
        }
        result_list.append(result_dict_temp)
    return result_list


def get_users(skip: int = 0, limit: int = 100):

    get_users_stmt = "SELECT username, email_id, phone, password FROM user LIMIT %S, %S"
    cur.execute(get_users_stmt, (skip, limit))
    result = cur.fetchall()
    result_list = []
    for i in range(len(result)):
        result_dict_temp = {
            "user_name": result[i][0],
            "email_id": result[i][1],
            "phone": result[i][2],
            "password": result[i][3],
        }
        result_list.append(result_dict_temp)
    return result_list


def create_user(user: us.User):

    create_user_stmt = (
        "INSERT INTO `user` (`username`, `email_id`, `phone`, `password`)"
        " VALUES (%s, %s, %s, %s)"
    )
    cur.execute(
        create_user_stmt, (user.user_name, user.email_id, user.phone, user.password)
    )
    get_connection().commit()
    print(cur.fetchall())
    result = get_user_by_user_name(user_name=user.user_name)
    return result


def delete_user_by_user_name(user_name: str):

    delete_by_username_stmt = "DELETE FROM user WHERE user.username=%s"
    cur.execute(delete_by_username_stmt, user_name)
    get_connection().commit()
    return user_name
