from model import flatmate
from dao import room_dao

from config.db import get_connection
from pymysql import MySQLError
from datetime import date

def create_flatmate(mate: flatmate.FlatmateBase):
    try:
        today = date.today()
        create_stmt = "INSERT INTO flatmate (username, flat_code, join_date) VALUES (%s, %s, %s)"

        with get_connection().cursor() as cur:
            cur.execute(create_stmt, (mate.username, mate.flat_code, today))

        return get_flatmate(mate.username)
    except MySQLError as e:
        raise ValueError(f"Error joining flat: {e}")

def get_flatmate(username: str):
    try:
        with get_connection().cursor() as cur:
            cur.callproc("get_flatmate", (username,))
            result = cur.fetchone()
        if not result:
            return None

        flatmate_model = flatmate.FlatmateWithRoomName(
            username=result[0],
            flat_code=result[1],
            room_name=result[2],
            join_date=result[3]
        )

        return flatmate_model
    except MySQLError as e:
        raise ValueError(f"Error getting flatmate details: {e}")
    

def get_flatmates_by_flat(flat_code: str):
    try:

        with get_connection().cursor() as cur:
            cur.callproc("get_flatmates_by_flat_code", (flat_code,))
            result = cur.fetchall()

        if not result:
            return None
    
        result_models = []
        
        for i in range(len(result)):
            
            flatmate_model = flatmate.FlatmateWithRoomName(
                username=result[i][0],
                flat_code=result[i][1],
                room_name=result[i][2],
                join_date=result[i][3]
            )
            result_models.append(flatmate_model)
            
        return result_models
    except MySQLError as e:
        raise ValueError(f"Error getting flatmates by flat: {e}")


def update_room(username: str, room_name: str):
    try:

        with get_connection().cursor() as cur:
            cur.callproc("update_flatmate_room", (username, room_name))

        return get_flatmate(username)
    except MySQLError as e:
        raise ValueError(f"Error updating room for flatmate: {e}")

def delete_flatmate(username: str):
    try:
        delete_stmt = "DELETE FROM flatmate WHERE username=%s"

        with get_connection().cursor() as cur:
            cur.execute(delete_stmt, (username,))

        return cur.rowcount > 0
    except MySQLError as e:
        raise ValueError(f"Error deleting flatmate: {e}")