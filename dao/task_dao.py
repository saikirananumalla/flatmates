from typing import Optional

import pymysql
from pydantic.schema import List
from datetime import datetime, timedelta

from model.task import CreateTask, UpdateTask, GetTask

from config.db import get_connection

cur = get_connection().cursor()


def create_task(task_details: CreateTask):
    
    task_created = False
    
    try: 
        
        # Date validation.
        task_date = datetime.strptime(task_details.task_date, "%Y-%m-%d")
        if task_date < datetime.now():
            raise ValueError("Invalid Date")

        # Check if the first person in the list is a valid member of the flat.
        cur.callproc("check_if_user_belongs_to_flat", (task_details.flat_code,
                                                        task_details.username_sequence[0]))
        first_user_exists = cur.fetchone()
        if not first_user_exists[0]:
            raise ValueError("Invalid username")

        # Inserting the task into the task table. Adding the first person as current_assigned_to.
        create_task_stmt = (
            "insert into task (task_name, frequency, current_assigned_to, task_date, flat_code) "
            "values (%s, %s, %s, %s, %s)"
        )
        cur.execute(create_task_stmt, (task_details.task_name, task_details.frequency,
                                        task_details.username_sequence[0], task_details.task_date,
                                        task_details.flat_code))
        
        task_created = True

        # Retrieving the task_id from the task_name and the flat_code.
        task_id = get_task_id_from_name_flat_code(task_details.task_name, task_details.flat_code)

        # Updating the task order for all the usernames in the list.
        # Should write failure fallback functions to undo the database.

        update_task_order(username_sequence=task_details.username_sequence,
                          flat_code=task_details.flat_code, task_id=task_id)
    except Exception as e:
        if task_created:
            delete_task(task_details.task_name, task_details.flat_code)
        raise ValueError(f"Error updating task: pls check your inputs" + str(e))

    return get_task_details(task_id)


def get_task(task_name: str, flat_code: str) -> GetTask:

    try:
        result_task_id = get_task_id_from_name_flat_code(task_name, flat_code)
        return get_task_details(result_task_id)
    except MySQLError as e:
        raise ValueError(f"Error getting task: pls check your inputs")


def update_task(update_task_details: UpdateTask):

    # Delete all the existing task orders.
    delete_task_order_by_task_id(update_task_details.task_id)

    # Get flat_code for input validation.
    get_flat_code_stmt = (
        "select flat_code from task where task_id=%s"
    )
    cur.execute(get_flat_code_stmt, update_task_details.task_id)
    flat_code = cur.fetchone()
    
    if flat_code is None:
        raise ValueError("Task Id does not exist")
    
    flat_code=flat_code[0]  
      
    # Check if the first person in the list is a valid member of the flat.
    cur.callproc("check_if_user_belongs_to_flat", (flat_code,
                                                   update_task_details.username_sequence[0]))
    first_user_exists = cur.fetchone()
    if not first_user_exists[0]:
        raise ValueError("Invalid username")

    # Update the task row.
    update_task_details_stmt = (
        "update task set task_name=%s, task_date=%s, frequency=%s, current_assigned_to=%s where task_id=%s"
    )
    cur.execute(update_task_details_stmt, (update_task_details.task_name,
                                           update_task_details.task_date,
                                           update_task_details.frequency,
                                           update_task_details.username_sequence[0],
                                           update_task_details.task_id))

    # Call update task orders for the new order.
    try:
        update_task_order(username_sequence=update_task_details.username_sequence,
                          flat_code=flat_code, task_id=update_task_details.task_id)
    except MySQLError as e:
        raise ValueError(f"Error creating task: pls check your inputs")

    return get_task_details(int(update_task_details.task_id))


#other flatmates can also update a task as done by user
def update_task_done_by_user(task_id: int):
    try:
        # Update the task row.
        cur.callproc("next_flatmate_to_perform_task", (task_id,))
        update_task_details_stmt = (
            "update task set task_date=%s, task_ended=%s, current_assigned_to=%s where task_id=%s"
        )
        
        res_user = cur.fetchone()
        if res_user is None:
            return None
        
        next_user = res_user[0]
        
        cur.execute("select frequency, task_date from task where task_id = %s", task_id)
        res = cur.fetchone()
        
        task_ended = False
        if (res[0] == 'NO_REPEAT'):
            task_ended = True
        
        get_new_task_date = getDateFromFreq(res[0], str(res[1]))
        cur.execute(update_task_details_stmt, (str(get_new_task_date), task_ended, next_user, str(task_id)))
        
        return get_task_details(task_id)
    except Exception as e:
        raise ValueError(f"Error updating task" + str(e))


def delete_task(task_id: int):

    try:
        
        # Delete the task row in the task table.
        delete_task_stmt = (
            "delete from task where task_id=%s"
        )
        cur.execute(delete_task_stmt, task_id)

        # Delete the subsequent rows in the task order table.
        # delete_task_order_by_task_id(task_id=task_id)
        return cur.rowcount > 0
    except Exception as e:
        raise ValueError("Task_id does not exist")


def get_task_details(task_id: int) -> GetTask:

    cur.callproc("get_all_task_details_by_task_id", (str(task_id),))
    result = cur.fetchall()
    
    if len(result)==0:
        raise ValueError("Task does not exist")

    # task.task_id, task_name, frequency, current_assigned_to, task_date, flat_code,
    # task_order_id, seq_number, username is the order of the result.
    temp_dict = {}
    result_list = []

    for row in result:
        if row[8] is not None and row[9] is not None:
            temp_dict[row[8]] = row[9]
    for i in sorted(temp_dict.keys()):
        result_list.append(temp_dict[i])

    result_task = GetTask(
        task_id=result[0][0],
        task_name=result[0][1],
        frequency=result[0][2],
        current_assigned_to=result[0][3],
        task_date=str(result[0][4]),
        flat_code=result[0][5],
        username_sequence=result_list
    )
    return result_task


def update_task_order(username_sequence: List[str], flat_code: str, task_id: str):

    insert_task_order_stmt = (
        "insert into task_order (seq_number, username, task_id) VALUES (%s, %s, %s)"
    )
    count = 1

    for username in username_sequence:

        cur.callproc("check_if_user_belongs_to_flat",
                    (flat_code, username,))
        user_exists = cur.fetchone()

        if not user_exists[0]:
            raise ValueError("Invalid username")

        cur.execute(insert_task_order_stmt, (count, username, task_id))
        count = count + 1


def delete_task_order_by_task_id(task_id: str):

    delete_task_order_stmt = (
        "delete from task_order where task_id=%s"
    )
    cur.execute(delete_task_order_stmt, task_id)


def get_task_id_from_name_flat_code(task_name: str, flat_code: str):

    get_task_stmt = "select task_id from task where task_name=%s and flat_code=%s"
    cur.execute(get_task_stmt,
                (task_name, flat_code))
    result_task_id = cur.fetchone()
    
    if result_task_id is None:
        raise ValueError("Task does not exist")
    
    task_id = result_task_id[0]
    return task_id


def get_task_details_by_flat_code(flat_code: str, date: Optional[str] = None):

    get_task_stmt = "select task_id from task where flat_code=%s"
    cur.execute(get_task_stmt,
                flat_code)
    result_task_ids = cur.fetchall()
    
    if len(result_task_ids) == 0:
        raise ValueError("No tasks found under the given flat code.")
    
    result = []
    
    for task_id in result_task_ids:
        result.append(get_task_details(task_id))

    if date is not None:
        return get_task_details_date(tasks=result, date=date)
    
    return result


def get_task_details_date(tasks: List[GetTask], date: str):

    result_tasks_for_date = []
    focus_date = datetime.strptime(date, '%Y-%m-%d')

    frequency_mapping = {
        'no_repeat': timedelta(days=0),
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'monthly': timedelta(days=30)
    }

    for task in tasks:

        delta = frequency_mapping.get(task.frequency.lower())
        task_date = datetime.strptime(task.task_date, '%Y-%m-%d')

        if abs(focus_date - task_date) % delta == 0:
            result_tasks_for_date.append(task)

    return result_tasks_for_date


def getDateFromFreq(frequency, current_date):
    # Convert the input date string to a datetime object
    current_date = datetime.strptime(current_date, '%Y-%m-%d')

    # Define a dictionary to map frequency strings to timedelta values
    frequency_mapping = {
        'no_repeat': timedelta(days=0),
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'monthly': timedelta(days=30)  # Assuming a month is approximately 30 days
    }

    # Get the corresponding timedelta for the given frequency
    delta = frequency_mapping.get(frequency.lower())

    if delta is not None:
        # Calculate the next date by adding the timedelta to the current date
        next_date = current_date + delta
        return next_date.strftime('%Y-%m-%d')  # Convert the result back to string format
    else:
        return "Invalid frequency"