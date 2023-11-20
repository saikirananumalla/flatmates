import datetime

from pydantic import BaseModel


class Task(BaseModel):

    task_id: int = None
    task_name: str
    frequency: str
    current_assigned_to: str
    task_date: datetime.datetime
    flat_code: str
