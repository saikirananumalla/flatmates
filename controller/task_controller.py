import datetime

from config.oauth import get_current_user
from dao import task_dao
from fastapi import APIRouter, HTTPException, Depends
from pydantic.schema import List
from typing import Union

from model import user
from model.task import GetTask, CreateTask, UpdateTask, BaseTask

task_router = APIRouter()


@task_router.post("/task/", response_model=GetTask, tags=["task"])
def create_task(
    task_details: BaseTask, current_user: user.AuthUser = Depends(get_current_user)
):
    try:
        create_task_model = CreateTask(task_name=task_details.task_name,
                                       frequency=task_details.frequency,
                                       task_date=task_details.task_date,
                                       username_sequence=task_details.username_sequence,
                                       flat_code=current_user.flat_code)
        create_task_result = task_dao.create_task(task_details=create_task_model)
        return create_task_result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@task_router.get("/task/{task_name}", response_model=GetTask, tags=["task"])
def get_task_details(
    task_name: str, current_user: user.AuthUser = Depends(get_current_user)
):
    try:
        get_task_details_result = task_dao.get_task(
            task_name=task_name, flat_code=current_user.flat_code
        )
        return get_task_details_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@task_router.get("/task/flat/all", response_model=List[GetTask], tags=["task"])
def get_task_details_by_flat_code(
    date: Union[str, None] = None, has_ended: Union[bool, None] = None,
    current_user: user.AuthUser = Depends(get_current_user),
):
    try:
        get_task_details_by_flat_code_result = task_dao.get_task_details_by_flat_code(
            flat_code=current_user.flat_code, date=date, has_ended=has_ended
        )
        return get_task_details_by_flat_code_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@task_router.get("/task/user/all", response_model=List[GetTask], tags=["task"])
def get_task_details_by_flatmate(
    date: Union[str, None] = None, has_ended: Union[bool, None] = None,
    current_user: user.AuthUser = Depends(get_current_user),
):
    try:
        get_task_details_by_flatmate_result = task_dao.get_task_details_by_flatmate(
            username=current_user.username, flat_code=current_user.flat_code, date=date, has_ended=has_ended
        )

        if get_task_details_by_flatmate_result is None:

            return []

        return get_task_details_by_flatmate_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@task_router.get("/task/user/all/summary", response_model=List[GetTask], tags=["task"])
def get_task_details_by_flatmate_summary(current_user: user.AuthUser = Depends(get_current_user)):
    try:
        result = []
        today_date = datetime.datetime.now()
        for i in range(8):
            focus_date = today_date + datetime.timedelta(days=i)
            focus_date = focus_date.strftime("%Y-%m-%d")
            get_task_details_by_flatmate_result = task_dao.get_task_details_by_flatmate(
                username=current_user.username, date=focus_date, flat_code=current_user.flat_code
            )
            if get_task_details_by_flatmate_result is None:
                continue
            for task in get_task_details_by_flatmate_result:
                result.append(task)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@task_router.put("/task/", response_model=GetTask, tags=["task"])
def update_task(
    update_task_details: UpdateTask,
    current_user: user.AuthUser = Depends(get_current_user),
):
    try:
        update_task_result = task_dao.update_task(
            update_task_details=update_task_details,
            flat_code_user=current_user.flat_code,
        )
        return update_task_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@task_router.put("/task/{task_id}", response_model=GetTask, tags=["task"])
def update_task_done(
    task_id: int, current_user: user.AuthUser = Depends(get_current_user)
):
    try:
        update_task_done_result = task_dao.update_task_done_by_user(
            task_id=task_id, flat_code_user=current_user.flat_code
        )
        return update_task_done_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@task_router.delete("/task/delete/{task_id}", response_model=str, tags=["task"])
def delete_task(task_id: int, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        delete_task_result = task_dao.delete_task(
            task_id=task_id, flat_code_user=current_user.flat_code
        )
        return delete_task_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
