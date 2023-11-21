from dao import task_dao
from fastapi import APIRouter


from model.task import GetTask, CreateTask, UpdateTask

task_router = APIRouter()


@task_router.post("/task/", response_model=GetTask, tags=["task"])
def create_task(task_details: CreateTask):
    create_task_result = task_dao.create_task(task_details=task_details)
    return create_task_result


@task_router.get("/task/{task_name}/{flat_code}", response_model=GetTask, tags=["task"])
def get_task_details(task_name: str, flat_code: str):
    get_task_details_result = task_dao.get_task(task_name=task_name, flat_code=flat_code)
    return get_task_details_result


@task_router.get("/task/{task_id}", response_model=GetTask, tags=["task"])
def get_task_details_by_task_id(task_id: int):
    result_task = task_dao.get_task_details(task_id=task_id)
    return result_task


@task_router.patch("/update_task", response_model=GetTask, tags=["task"])
def update_task(update_task_details: UpdateTask):
    update_task_result = task_dao.update_task(update_task_details=update_task_details)
    return update_task_result


@task_router.delete("/delete_task/{task_name}/{flat_code}", response_model=str,
                    tags=["task"])
def delete_task(task_name: str, flat_code: str):
    delete_task_result = task_dao.delete_task(task_name=task_name, flat_code=flat_code)
    return delete_task_result

