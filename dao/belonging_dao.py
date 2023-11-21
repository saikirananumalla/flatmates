from model import belonging

from config.db import get_connection
from pymysql import MySQLError

def create_belonging(belonging: belonging.Belonging):
    cur = get_connection().cursor()
    try:
        cur.callproc('insert_belonging', (belonging.description, belonging.name, belonging.flat_code,))

        result = cur.fetchone()
        
        if result is None:
            return None
        
        belonging_id = result[0]
        
        
        try:
            for owner in belonging.owners:
                cur.callproc('add_belonging_owner', (belonging_id, owner))
        except MySQLError as ex:
            delete_belonging(belonging_id)
            raise ex
        
        return get_belonging(belonging.name, belonging.flat_code)
        
    except MySQLError as e:
        raise ValueError(f"Error creating belonging: {e}")

def get_belonging(name: str, flat_code: str):
    try:
        with get_connection().cursor() as cur:
            cur.callproc("get_belonging", (name, flat_code))
            result = cur.fetchone()
        if result is None:
            return None
        
        belonging_model = belonging.BelongingStr(
            belonging_id=result[0],
            descrition=result[1],
            name=result[2],
            flat_code=result[3],
            owners=result[4]
        )
        
        return belonging_model

        
    except MySQLError as e:
        raise ValueError(f"Error getting belonging details: {e}")
    

def get_belonging_by_id(belonging_id: int):
    try:
        with get_connection().cursor() as cur:
            cur.execute("SELECT name, flat_code from belonging where belonging_id=%s", (belonging_id))
        result = cur.fetchone()
        if result is None:
            return None
        
        return get_belonging(result[0], result[1])

        
    except MySQLError as e:
        raise ValueError(f"Error getting belonging details: {e}")
    

def get_belongings_by_flat(flat_code: str):
    try:

        with get_connection().cursor() as cur:
            cur.callproc("get_belonging_by_flat", (flat_code,))
            result = cur.fetchall()

        if not result:
            return None
    
        result_models = []
        
        for i in range(len(result)):
            
            belonging_model = belonging.BelongingStr(
                belonging_id=result[i][0],
                description=result[i][1],
                name=result[i][2],
                flat_code=result[i][3],
                owners=result[i][4]
            )
            result_models.append(belonging_model)
            
        return result_models
    except MySQLError as e:
        raise ValueError(f"Error getting belongings by flat: {e}")


def update_belonging(belonging_id: int, belonging: belonging.UpdateBelonging):
    cur = get_connection().cursor()
    try:
        cur.callproc("update_belonging", (belonging_id, belonging.description, belonging.name))

        cur.callproc("drop_belonging_owners", (belonging_id,))
        
        for owner in belonging.owners:
            cur.callproc('add_belonging_owner', (belonging_id, owner))
        
        return get_belonging_by_id(belonging_id)
        
    except MySQLError as e:
        raise ValueError(f"Error updating belonging: {e}")

def delete_belonging(belonging_id: int):
    try:
        delete_stmt = "DELETE FROM belonging WHERE belonging_id=%s"

        with get_connection().cursor() as cur:
            cur.execute(delete_stmt, (belonging_id,))

        return cur.rowcount > 0
    except MySQLError as e:
        raise ValueError(f"Error deleting belonging: {e}")