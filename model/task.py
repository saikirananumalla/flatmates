import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic.schema import List


class BaseTask(BaseModel):

    task_name: str
    frequency: str
    task_date: str
    username_sequence: Optional[List[str]] = None


class CreateTask(BaseTask):

    flat_code: str


class UpdateTask(BaseTask):

    task_id: str


class GetTask(CreateTask, UpdateTask):

    current_assigned_to: Optional[str] = None


class TaskOrder(BaseModel):

    seq_number: int
    username: str
    task_id: str
