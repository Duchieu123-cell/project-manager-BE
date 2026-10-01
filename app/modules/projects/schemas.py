from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.core.enum_data import TaskStatusEnum, TaskPriorityEnum

class ProjectBase(BaseModel):
    name: str
    description: str
    difficulty: int
    isAccepted: bool

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    difficulty: int | None = None
    isAccepted: bool | None = None

class ProjectResponse(ProjectBase):
    id: int
    createdAt: datetime
    lastModified: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    name: str
    description: str
    status: TaskStatusEnum
    priority: TaskPriorityEnum
    dueDate: datetime

class TaskCreate(TaskBase):
    projectId: int

class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: TaskStatusEnum | None = None
    priority: TaskPriorityEnum | None = None
    dueDate: datetime | None = None

class TaskResponse(TaskBase):
    id: int
    projectId: int
    createdAt: datetime
    lastModified: datetime
    
    model_config = ConfigDict(from_attributes=True)