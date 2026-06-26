from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

# --- Task Schemas ---
class TaskBase(BaseModel):
    task_description: str
    assignee: Optional[str] = None
    deadline: Optional[str] = None
    is_completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    meeting_id: int

    # Pydantic V2 replacement for orm_mode = True
    model_config = ConfigDict(from_attributes=True)

# --- Meeting Schemas ---
class MeetingBase(BaseModel):
    title: str = Field(..., max_length=255)

class MeetingCreate(MeetingBase):
    transcript: Optional[str] = None

class MeetingResponse(MeetingBase):
    id: int
    status: str
    created_at: datetime
    tasks: List[TaskResponse] = []

    model_config = ConfigDict(from_attributes=True)
