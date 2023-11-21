import datetime

import pymysql
from pydantic.schema import List

from model.task import CreateTask, UpdateTask, GetTask

from config.db import get_connection

cur = get_connection().cursor()


def create_task(task_details: CreateTask):

    # Date validation.
    task_date = datetime.datetime.strptime(task_details.task_date, "%Y-%m-%d")
    if task_date < datetime.datetime.now():
        print("Invalid task date, cannot be less than today")
        raise Exception("Invalid Date")

    # Check if the first person in the list is a valid member of the flat.
    cur.callproc("check_if_user_belongs_to_flat", (task_details.flat_code,
                                                   task_details.username_sequence[0]))
    first_user_exists = cur.fetchone()
    if not first_user_exists[0]:
        print("Invalid username, does not belong to the flat")
        raise Exception("Invalid username")

    # Inserting the task into the task table. Adding the first person as current_assigned_to.
    create_task_stmt = (
        "insert into task (task_name, frequency, current_assigned_to, task_date, flat_code) "
        "values (%s, %s, %s, %s, %s)"
    )
    cur.execute(create_task_stmt, (task_details.task_name, task_details.frequency,
                                   task_details.username_sequence[0], task_details.task_date,
                                   task_details.flat_code))

    # Retrieving the task_id from the task_name and the flat_code.
    task_id = get_task_id_from_name_flat_code(task_details.task_name, task_details.flat_code)

    # Updating the task order for all the usernames in the list.
    # Should write failure fallback functions to undo the database.
    try:

        update_task_order(username_sequence=task_details.username_sequence,
                          flat_code=task_details.flat_code, task_id=task_id)
    except pymysql.Error as pe:

        delete_task(task_details.task_name, task_details.flat_code)
        raise pe

    return get_task_details(task_id)


def get_task(task_name: str, flat_code: str) -> GetTask:

    try:
        result_task_id = get_task_id_from_name_flat_code(task_name, flat_code)
        return get_task_details(result_task_id)
    except pymysql.Error as pe:
        raise pe


def update_task(update_task_details: UpdateTask):

    # Delete all the existing task orders.
    delete_task_order_by_task_id(update_task_details.task_id)

    # Update the task row.
    update_task_details_stmt = (
        "update task set task_name=%s, task_date=%s, frequency=%s where task_id=%s"
    )
    cur.execute(update_task_details_stmt, (update_task_details.task_name,
                                           update_task_details.task_date,
                                           update_task_details.frequency,
                                           update_task_details.task_id))

    # Get flat_code for input validation.
    get_flat_code_stmt = (
        "select flat_code from task where task_id=%s"
    )
    cur.execute(get_flat_code_stmt, update_task_details.task_id)
    flat_code = cur.fetchone()[0]

    # Call update task orders for the new order.
    try:
        update_task_order(username_sequence=update_task_details.username_sequence,
                          flat_code=flat_code, task_id=update_task_details.task_id)
    except pymysql.Error as pe:
        raise pe

    return get_task_details(int(update_task_details.task_id))


def delete_task(task_name: str, flat_code: str):

    # get the task id from the task name and the flat code.
    task_id = get_task(task_name, flat_code).task_id

    # Delete the task row in the task table.
    delete_task_stmt = (
        "delete from task where task_id=%s"
    )
    cur.execute(delete_task_stmt, task_id)

    # Delete the subsequent rows in the task order table.
    delete_task_order_by_task_id(task_id=task_id)
    return "OK"


def get_task_details(task_id: int) -> GetTask:

    cur.callproc("get_all_task_details_by_task_id", (str(task_id),))
    result = cur.fetchall()

    # task.task_id, task_name, frequency, current_assigned_to, task_date, flat_code,
    # task_order_id, seq_number, username is the order of the result.
    temp_dict = {}
    result_list = []

    for row in result:
        temp_dict[row[7]] = row[8]
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
            print("Invalid username, does not belong to the flat")
            raise Exception("Invalid username")

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
    task_id = result_task_id[0]
    return task_id
