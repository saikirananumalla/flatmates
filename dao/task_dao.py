from typing import Optional

from pydantic.schema import List
from datetime import datetime, timedelta

from pymysql import MySQLError

from model.task import CreateTask, UpdateTask, GetTask

from config.db import get_connection


def create_task(task_details: CreateTask):

    task_created = False
    task_id = None
    try:
        with get_connection().cursor() as cur:
            # Date validation.
            task_date = datetime.strptime(task_details.task_date, "%Y-%m-%d")
            if task_date.date() < datetime.now().date():
                raise ValueError("Invalid Date")

            # Check if the first person in the list is a valid member of the flat.
            cur.callproc(
                "check_if_user_belongs_to_flat",
                (task_details.flat_code, task_details.username_sequence[0]),
            )
            first_user_exists = cur.fetchone()
            if not first_user_exists[0]:
                raise ValueError("Invalid username")

            # Inserting the task into the task table. Adding the first person as current_assigned_to.
            create_task_stmt = (
                "insert into task (task_name, frequency, current_assigned_to, task_date, flat_code) "
                "values (%s, %s, %s, %s, %s)"
            )
            cur.execute(
                create_task_stmt,
                (
                    task_details.task_name,
                    task_details.frequency,
                    task_details.username_sequence[0],
                    task_details.task_date,
                    task_details.flat_code,
                ),
            )

            task_created = True

            # Retrieving the task_id from the task_name and the flat_code.
            task_id = get_task_id_from_name_flat_code(
                task_details.task_name, task_details.flat_code
            )

            # Updating the task order for all the usernames in the list.
            # Should write failure fallback functions to undo the database.

            update_task_order(
                username_sequence=task_details.username_sequence,
                flat_code=task_details.flat_code,
                task_id=task_id,
            )
    except Exception as e:
        if task_created:
            delete_task(task_id=task_id, flat_code_user=task_details.flat_code)
        raise ValueError(f"Error updating task: pls check your inputs" + str(e))

    return get_task_details(task_id)


def get_task(task_name: str, flat_code: str) -> GetTask:

    try:
        result_task_id = get_task_id_from_name_flat_code(task_name, flat_code)
        return get_task_details(result_task_id)
    except Exception:
        raise ValueError(f"Error getting task: pls check your inputs")


def update_task(update_task_details: UpdateTask, flat_code_user: str):

    with get_connection().cursor() as cur:
        # Get flat_code for input validation.
        get_flat_code_stmt = "select flat_code from task where task_id=%s"
        
        cur.execute(get_flat_code_stmt, update_task_details.task_id)
        flat_code = cur.fetchone()

        if flat_code[0] != flat_code_user:
            raise ValueError("User not authorized")

        # Delete all the existing task orders.
        delete_task_order_by_task_id(update_task_details.task_id)

        if flat_code is None:
            raise ValueError("Task Id does not exist")

        flat_code = flat_code[0]

        # Check if the first person in the list is a valid member of the flat.
        cur.callproc(
            "check_if_user_belongs_to_flat",
            (flat_code, update_task_details.username_sequence[0]),
        )
        first_user_exists = cur.fetchone()
        if not first_user_exists[0]:
            raise ValueError("Invalid username")

        # Update the task row.
        update_task_details_stmt = ("update task set task_name=%s, task_date=%s, frequency=%s,"
                                    " current_assigned_to=%s where task_id=%s")
        cur.execute(
            update_task_details_stmt,
            (
                update_task_details.task_name,
                update_task_details.task_date,
                update_task_details.frequency,
                update_task_details.username_sequence[0],
                update_task_details.task_id,
            ),
        )

    # Call update task orders for the new order.
    try:
        update_task_order(
            username_sequence=update_task_details.username_sequence,
            flat_code=flat_code,
            task_id=update_task_details.task_id,
        )
    except MySQLError:
        raise ValueError(f"Error creating task: pls check your inputs")

    return get_task_details(int(update_task_details.task_id))


# other flatmates can also update a task as done by user
def update_task_done_by_user(task_id: int, flat_code_user: str):
    try:
        with get_connection().cursor() as cur:
            # Update the task row.
            cur.callproc("next_flatmate_to_perform_task", (task_id,))
            update_task_details_stmt = ("update task set task_date=%s, task_ended=%s,"
                                        " current_assigned_to=%s where task_id=%s")

            res_user = cur.fetchone()
            if res_user is None:
                return None

            next_user = res_user[0]

            cur.execute(
                "select frequency, task_date, flat_code from task where task_id = %s",
                task_id,
            )
            res = cur.fetchone()

            if res[2] != flat_code_user:
                raise ValueError("User not authorized to update the task")

            task_ended = False
            if res[0] == "NO_REPEAT":  
                task_ended = True

            get_new_task_date = getDateFromFreq(res[0], str(res[1]))
            cur.execute(
                update_task_details_stmt,
                (str(get_new_task_date), task_ended, next_user, str(task_id)),
            )

            return get_task_details(task_id)
    except Exception as e:
        raise ValueError(f"Error updating task" + str(e))


def delete_task(task_id: int, flat_code_user: str):

    try:
        with get_connection().cursor() as cur:
            cur.execute("select flat_code from task where task_id = %s", task_id)

            res = cur.fetchone()
            if res[0] != flat_code_user:
                raise ValueError("User not authorized to delete the task")

            # Delete the task row in the task table.
            delete_task_stmt = "delete from task where task_id=%s"
            cur.execute(delete_task_stmt, task_id)

            # Delete the subsequent rows in the task order table.
            # delete_task_order_by_task_id(task_id=task_id)
            return cur.rowcount > 0
    except Exception:
        raise ValueError("Task_id does not exist" + str(task_id))


def get_task_details(task_id: int) -> GetTask:

    with get_connection().cursor() as cur:
        cur.callproc("get_all_task_details_by_task_id", (task_id,))
        result = cur.fetchall()

        if len(result) == 0:
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
            username_sequence=result_list,
        )
        return result_task


def update_task_order(username_sequence: List[str], flat_code: str, task_id: str):

    insert_task_order_stmt = (
        "insert into task_order (seq_number, username, task_id) VALUES (%s, %s, %s)"
    )
    count = 1
    
    with get_connection().cursor() as cur:

        for username in username_sequence:

            cur.callproc(
                "check_if_user_belongs_to_flat",
                (
                    flat_code,
                    username,
                ),
            )
            user_exists = cur.fetchone()

            if not user_exists[0]:
                raise ValueError("Invalid username")

            cur.execute(insert_task_order_stmt, (count, username, task_id))
            count = count + 1


def delete_task_order_by_task_id(task_id: str):

    delete_task_order_stmt = "delete from task_order where task_id=%s"
    with get_connection().cursor() as cur:
        cur.execute(delete_task_order_stmt, task_id)


def get_task_id_from_name_flat_code(task_name: str, flat_code: str):

    with get_connection().cursor() as cur:
        get_task_stmt = "select task_id from task where task_name=%s and flat_code=%s"
        cur.execute(get_task_stmt, (task_name, flat_code))
        result_task_id = cur.fetchone()

        if result_task_id is None:
            raise ValueError("Task does not exist")

        task_id = result_task_id[0]
        return task_id


def get_task_details_by_flat_code(flat_code: str, date: Optional[str] = None):
    with get_connection().cursor() as cur:

        get_task_stmt = "select task_id from task where flat_code=%s"
        cur.execute(get_task_stmt, flat_code)
        result_task_ids = cur.fetchall()

        if len(result_task_ids) == 0:
            return []

        result = []

        for task_id in result_task_ids:
            result.append(get_task_details(task_id[0]))

        if date is not None:
            return get_task_details_date(tasks=result, date=date)

        return result


def is_user_current_user_for_date(current_date, current_assigned_user, frequency,
                                  task_date, focus_user, sequence) -> bool:

    start_point = 0
    current_date = datetime.strptime(current_date, "%Y-%m-%d")
    task_date = datetime.strptime(task_date, "%Y-%m-%d")

    if current_date < task_date:
        return False

    if frequency.lower() == "no_repeat":
        if task_date == current_date:
            return True
        else:
            return False

    for i in range(len(sequence)):
        if sequence[i] == current_assigned_user:
            start_point = i

    frequency_mapping = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
        }

    unit_step = frequency_mapping.get(frequency.lower())
    date_check = abs(current_date - task_date).days % unit_step
    if date_check != 0:
        return False
    date_diff = abs(current_date - task_date).days // unit_step
    total_step = start_point + date_diff
    total_step = total_step % len(sequence)

    if sequence[total_step] == focus_user:
        return True
    else:
        return False


def get_task_details_by_flatmate(username: str, flat_code: str,  date: Optional[str] = None):

    with get_connection().cursor() as cur:
        if date is None:
            result = []
            get_task_stmt = "select task_id from task where current_assigned_to=%s"
            cur.execute(get_task_stmt, username)
            result_task_ids = cur.fetchall()
            if len(result_task_ids) == 0:
                return []
            for task_id in result_task_ids:
                result.append(get_task_details(task_id[0]))
            return result
        else:

            result = []
            get_task_stmt_by_flat = ("select task_id, current_assigned_to, frequency, task_date"
                                     " from task where flat_code=%s and task_ended=0")
            cur.execute(get_task_stmt_by_flat, flat_code)

            result_task_details = cur.fetchall()
            if len(result_task_details) == 0:
                return []
            result_task_ids_for_date = []
            for flat_task_detail in result_task_details:

                sequence = get_sequence_list(task_id=flat_task_detail[0])
                if username in sequence:
                    task_date = str(flat_task_detail[3])
                    if is_user_current_user_for_date(current_date=date,
                                                     current_assigned_user=flat_task_detail[1],
                                                     frequency=flat_task_detail[2],
                                                     task_date=task_date,
                                                     focus_user=username,
                                                     sequence=sequence):

                        result_task_ids_for_date.append(flat_task_detail[0])

                    else:
                        continue
                else:
                    continue

            for task_id in result_task_ids_for_date:
                task = get_task_details(task_id)
                task.task_date = date
                result.append(task)
                
            return result


def get_sequence_list(task_id: str) -> List[str]:
    with get_connection().cursor() as cur:
        get_task_order_stmt = "select username, seq_number from task_order where task_id=%s"
        cur.execute(get_task_order_stmt, task_id)
        result = cur.fetchall()
        result = list(result)
        if len(result) == 0:
            return []
        result.sort(key=lambda x: x[1])
        return [username[0] for username in result]


def get_task_details_date(tasks: List[GetTask], date: str):

    result_tasks_for_date = []
    focus_date = datetime.strptime(date, "%Y-%m-%d")

    frequency_mapping = {
        "no_repeat": timedelta(days=0),
        "daily": timedelta(days=1),
        "weekly": timedelta(weeks=1),
        "monthly": timedelta(days=30),
    }

    for task in tasks:

        delta = frequency_mapping.get(task.frequency.lower())
        task_date = datetime.strptime(task.task_date, "%Y-%m-%d")

        date_dif = abs(focus_date - task_date).days

        if date_dif == 0:
            result_tasks_for_date.append(task)
        elif date_dif != 0 and task.frequency == "NO_REPEAT":
            continue
        elif date_dif % delta.days == 0:
            task.task_date = date
            result_tasks_for_date.append(task)

    return result_tasks_for_date


def getDateFromFreq(frequency, current_date):
    # Convert the input date string to a datetime object
    current_date = datetime.strptime(current_date, "%Y-%m-%d")

    # Define a dictionary to map frequency strings to timedelta values
    frequency_mapping = {
        "no_repeat": timedelta(days=0),
        "daily": timedelta(days=1),
        "weekly": timedelta(weeks=1),
        "monthly": timedelta(days=30),  # Assuming a month is approximately 30 days
    }

    # Get the corresponding timedelta for the given frequency
    delta = frequency_mapping.get(frequency.lower())

    if delta is not None:
        # Calculate the next date by adding the timedelta to the current date
        next_date = current_date + delta
        return next_date.strftime(
            "%Y-%m-%d"
        )  # Convert the result back to string format
    else:
        return "Invalid frequency"
