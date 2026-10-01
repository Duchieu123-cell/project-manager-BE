from app.modules.projects import schemas, models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from fastapi import HTTPException, status

class ProjectService:

    @staticmethod
    async def get_all_projects(db: AsyncSession) -> list[models.Project]:
        projects = (await db.execute(select(models.Project))).scalars().all()
        
        return projects

    @staticmethod
    async def create_project(project_data: schemas.ProjectCreate, db: AsyncSession) -> models.Project:
        new_project = models.Project(
            name=project_data.name,
            description=project_data.description,
            difficulty=project_data.difficulty,
            isAccepted=project_data.isAccepted
        )
        db.add(new_project)
        await db.flush()
        await db.refresh(new_project)
        
        return new_project
    
    @staticmethod
    async def delete_project(project_id: int, db: AsyncSession) -> models.Project:
        project = await db.get(models.Project, project_id)
        if not project:
            return None
        
        await db.delete(project)
        await db.flush()
        
        return project
    
    @staticmethod
    async def update_project(project_data: schemas.ProjectUpdate, project_id: int, db: AsyncSession) -> models.Project:
        project = await db.get(models.Project, project_id)
        if not project:
            return None
        
        project_data_dict = project_data.model_dump(exclude_unset=True)
        
        for key, value in project_data_dict.items():
            if value is not None:
                setattr(project, key, value)
                
        project.lastModified = datetime.now(timezone.utc)
                
        await db.flush()
        return project
    
class TaskService:

    @staticmethod
    async def get_all_tasks(db: AsyncSession) -> list[models.Task]:
        tasks = (await db.execute(select(models.Task))).scalars().all()
        
        return tasks
    
    @staticmethod
    async def get_tasks_of_project(project_id: int, db: AsyncSession) -> list[models.Task]:
        # Kiem tra xem dự án có tồn tại không
        project = await db.get(models.Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy project có ID: {project_id}"
            )
        
        tasks = (await db.execute(select(models.Task).where(models.Task.projectId == project_id))).scalars().all()
        
        if not tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy nhiệm vụ nào cho project có ID là {project_id}"
            )
        
        return tasks

    @staticmethod
    async def create_task(task_data: schemas.TaskCreate, db: AsyncSession) -> models.Task:
        new_task = models.Task(
            name=task_data.name,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            dueDate=task_data.dueDate,
            projectId=task_data.projectId
        )
        db.add(new_task)
        await db.flush()
        await db.refresh(new_task)
        
        return new_task

    @staticmethod
    async def delete_task(task_id: int, db: AsyncSession) -> models.Task:
        task = await db.get(models.Task, task_id)
        if not task:
            return None
        
        await db.delete(task)
        await db.flush()
        
        return task
    
    @staticmethod
    async def update_task(task_data: schemas.TaskUpdate, task_id: int, db: AsyncSession) -> models.Task:
        task = await db.get(models.Task, task_id)
        if not task:
            return None
        
        task_data_dict = task_data.model_dump(exclude_unset=True)
        
        for key, value in task_data_dict.items():
            if value:
                setattr(task, key, value)
                
        task.lastModified = datetime.now(timezone.utc)
                
        await db.flush()
        return task