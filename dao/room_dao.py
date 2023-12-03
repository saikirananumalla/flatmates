from model import room


from config.db import get_connection
from pymysql import MySQLError

def create_room(room: room.RoomWithoutId):
    try:
        create_stmt = "INSERT INTO room (name, flat_code) VALUES (%s, %s)"

        with get_connection().cursor() as cur:
            cur.execute(create_stmt, (room.name, room.flat_code))

        return get_room(room.name, room.flat_code)
    except MySQLError as e:
        raise ValueError(f"Error creating room: pls check your inputs")

def get_room(name: str, flat_code: str):
    try:
        get_room_stmt = "SELECT * FROM room WHERE name=%s AND flat_code=%s"

        with get_connection().cursor() as cur:
            cur.execute(get_room_stmt, (name, flat_code))
            result = cur.fetchone()

        if not result:
            return None

        room_model = room.Room(
            room_id=result[0],
            name=result[1],
            flat_code=result[2]
        )

        return room_model
    except MySQLError as e:
        raise ValueError(f"Error getting room: pls check your inputs")
    

def get_rooms_by_flat(flat_code: str):
    try:
        get_all_stmt = "SELECT * FROM room WHERE room.flat_code=%s"

        with get_connection().cursor() as cur:
            cur.execute(get_all_stmt, (flat_code))
            result = cur.fetchall()

        if not result:
            return None
    
        result_models = []
        
        for i in range(len(result)):
            room_model = room.Room(
                room_id=result[i][0],
                name=result[i][1],
                flat_code=result[i][2]
            )
            result_models.append(room_model)
            
        return result_models
    except MySQLError as e:
        raise ValueError(f"Error getting room by flat: pls check your inputs")


def update_room_name(room_id: int, name: str, flat_code: str):
    try:
        validate_room_id_with_flat_code(room_id, flat_code)
        update_name_stmt = "UPDATE room SET name=%s WHERE room_id=%s"

        with get_connection().cursor() as cur:
            cur.execute(update_name_stmt, (name, room_id))

        return get_room_by_id(room_id)
    except MySQLError as e:
        raise ValueError(f"Error updating room: pls check your inputs")

def delete_room(room_id: str, flat_code: str):
    try:
        validate_room_id_with_flat_code(room_id, flat_code)
        delete_stmt = "DELETE FROM room WHERE room_id=%s"

        with get_connection().cursor() as cur:
            cur.execute(delete_stmt, (room_id,))

        return cur.rowcount > 0
    except MySQLError as e:
        raise ValueError(f"Error deleting flat: pls check your inputs")



def get_room_by_id(room_id: int):
    try:
        get_room_stmt = "SELECT * FROM room WHERE room_id=%s"

        with get_connection().cursor() as cur:
            cur.execute(get_room_stmt, (room_id,))
            result = cur.fetchone()

        if not result:
            return None

        room_model = room.Room(
            room_id=result[0],
            name=result[1],
            flat_code=result[2]
        )

        return room_model
    except MySQLError as e:
        raise ValueError(f"Error getting room: pls check your inputs")
    
    
def validate_room_id_with_flat_code(room_id: int, flat_code: str):
    try:
        get_room_stmt = "SELECT flat_code FROM room WHERE room_id=%s"

        with get_connection().cursor() as cur:
            cur.execute(get_room_stmt, (room_id,))
            result = cur.fetchone()

        if not result:
            raise ValueError(f"Error getting room: room_id not found")

        if(result[0] != flat_code):
            raise ValueError(f"Error getting room: invalid room_id for this flat")

    except MySQLError as e:
        raise ValueError(f"Error getting room: invalid user or details")