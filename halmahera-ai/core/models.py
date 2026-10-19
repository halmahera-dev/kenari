from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    scholarship_id: str
    status: str = "on-progress"


class TaskCreate(BaseModel):
    name: str
    application_id: str
    description: Optional[str] = None
    is_completed: bool = False
    start_date: str = Field(
        ...,
        description="The start date of the task in YYYY-MM-DD format. Example: 2025-11-13"
    )
    end_date: str = Field(
        ...,
        description="The start date of the task in YYYY-MM-DD format. Example: 2025-12-30"
    )