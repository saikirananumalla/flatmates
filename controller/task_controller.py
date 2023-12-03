from typing import Union

from dao import task_dao
from fastapi import APIRouter, HTTPException
from pydantic.schema import List
from typing import Union


from model.task import GetTask, CreateTask, UpdateTask

task_router = APIRouter()


@task_router.post("/task/", response_model=GetTask, tags=["task"])
def create_task(task_details: CreateTask):
    try:
        create_task_result = task_dao.create_task(task_details=task_details)
        return create_task_result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@task_router.get("/task/{task_name}/{flat_code}", response_model=GetTask, tags=["task"])
def get_task_details(task_name: str, flat_code: str):
    try:
        get_task_details_result = task_dao.get_task(task_name=task_name, flat_code=flat_code)
        return get_task_details_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))   
    

@task_router.get("/task/{flat_code}", response_model=List[GetTask], tags=["task"])
def get_task_details_by_flat_code(flat_code: str, date: Union[str, None] = None):
    try:
        get_task_details_by_flat_code_result = (
            task_dao.get_task_details_by_flat_code(flat_code=flat_code, date=date))
        return get_task_details_by_flat_code_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
        

@task_router.get("/task/user/{username}", response_model=List[GetTask], tags=["task"])
def get_task_details_by_flatmate(username: str):
    try:
        get_task_details_by_flatmate_result = task_dao.get_task_details_by_flatmate(username=username)
        return get_task_details_by_flatmate_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@task_router.patch("/update_task", response_model=GetTask, tags=["task"])
def update_task(update_task_details: UpdateTask):
    try:
        update_task_result = task_dao.update_task(update_task_details=update_task_details)
        return update_task_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@task_router.patch("/update_task_done/{task_id}", response_model=GetTask,
                    tags=["task"])
def update_task_done(task_id: int):
    try:
        update_task_done_result = task_dao.update_task_done_by_user(task_id=task_id)
        return update_task_done_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@task_router.delete("/delete_task/{task_id}", response_model=str,
                    tags=["task"])
def delete_task(task_id: int):
    try:
        delete_task_result = task_dao.delete_task(task_id=task_id)
        return delete_task_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

