from model import flat
import string
import random

from config.db import get_connection
from pymysql import MySQLError

def create_flat(name: str):
    try:
        flat_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        create_stmt = "INSERT INTO flat (flat_code, name) VALUES (%s, %s)"

        with get_connection().cursor() as cur:
            cur.execute(create_stmt, (flat_code, name))

        return get_flat(flat_code)
    except MySQLError as e:
        raise ValueError(f"Error creating flat: pls check your inputs")

def get_flat(flat_code: str):
    try:
        get_flat_stmt = "SELECT * FROM flat WHERE flat.flat_code=%s"

        with get_connection().cursor() as cur:
            cur.execute(get_flat_stmt, flat_code)
            result = cur.fetchone()

        if not result:
            return None

        flat_model = flat.Flat(
            flat_code=result[0],
            name=result[1]
        )

        return flat_model
    except MySQLError as e:
        raise ValueError(f"Error getting flat: pls check your inputs")

def update_flat_name(flat: flat.Flat):
    try:
        flat_code = flat.flat_code
        update_name_stmt = "UPDATE flat SET name=%s WHERE flat_code=%s"

        with get_connection().cursor() as cur:
            cur.execute(update_name_stmt, (flat.name, flat_code))

        return get_flat(flat_code)
    except MySQLError as e:
        raise ValueError(f"Error updating flat: pls check your inputs")

def delete_flat_by_code(flat_code: str) -> bool:
    try:
        delete_stmt = "DELETE FROM flat WHERE flat_code=%s"

        with get_connection().cursor() as cur:
            cur.execute(delete_stmt, (flat_code,))

        return cur.rowcount > 0
    except MySQLError as e:
        raise ValueError(f"Error deleting flat: pls check your inputs")
