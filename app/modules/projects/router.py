from fastapi import APIRouter, HTTPException, status
from app.modules.projects import schemas
from app.core.dependencies import (
    DBSession,
    CREATE_PROJECT_PERMISSION,
    VIEW_PROJECT_PERMISSION,
    UPDATE_PROJECT_PERMISSION,
    DELETE_PROJECT_PERMISSION,
    CREATE_TASK_PERMISSION,
    VIEW_TASK_PERMISSION,
    UPDATE_TASK_PERMISSION,
    DELETE_TASK_PERMISSION
)
from fastapi import Depends, Path, Query
from app.modules.users import models
from typing import Annotated
from app.modules.projects.service import ProjectService, TaskService

project_router = APIRouter(
    prefix="/projects",
    tags=["projects"]
    
)

task_router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
    
)


@project_router.get(
    "",
    response_model=list[schemas.ProjectResponse],
    summary="Lấy danh sách tất cả dự án",
)
async def get_all_projects(
    db: DBSession,
    current_user: VIEW_PROJECT_PERMISSION
):
    return await ProjectService.get_all_projects(db)


@project_router.post(
    "",
    response_model=schemas.ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm một dự án mới",
)
async def create_project(
    project_data: schemas.ProjectCreate,
    db: DBSession,
    current_user: CREATE_PROJECT_PERMISSION
):
    return await ProjectService.create_project(project_data, db)


@project_router.delete(
    "/{project_id}",
    response_model=schemas.ProjectResponse,
    summary="Xóa một dự án",
)
async def delete_project(
    project_id: Annotated[int, Path()],
    db: DBSession,
    current_user: DELETE_PROJECT_PERMISSION
):
    result = await ProjectService.delete_project(project_id, db)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Không tìm thấy project có ID: {project_id}"
        )
        
    return result

@project_router.patch(
    "/{project_id}",
    response_model=schemas.ProjectResponse,
    summary="Cập nhật vài thuộc tính thông tin của dự án",
)
async def update_project(
    project_id: Annotated[int, Path()],
    project_data: schemas.ProjectUpdate,
    db: DBSession,
    current_user: UPDATE_PROJECT_PERMISSION
):
    result = await ProjectService.update_project(project_data, project_id, db)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Không tìm thấy project có ID: {project_id}"
        )
        
    return result

# Task router
@task_router.get(
    "",
    response_model=list[schemas.TaskResponse],
    summary="Lấy danh sách các nhiệm vụ",
)
async def get_tasks(
    db: DBSession,
    current_user: VIEW_TASK_PERMISSION,
    projectId: Annotated[int | None, Query()] = None
):
    if projectId:
        return await TaskService.get_tasks_of_project(projectId, db)
        
    return await TaskService.get_all_tasks(db)
    

@task_router.post(
    "",
    response_model=schemas.TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm một nhiệm vụ mới",
)
async def create_task(
    task_data: schemas.TaskCreate,
    db: DBSession,
    current_user: CREATE_TASK_PERMISSION
):
    return await TaskService.create_task(task_data, db)


@task_router.delete(
    "/{task_id}",
    response_model=schemas.TaskResponse,
    summary="Xóa một nhiệm vụ",
)
async def delete_task(
    task_id: Annotated[int, Path()],
    db: DBSession,
    current_user: DELETE_TASK_PERMISSION
):
    result = await TaskService.delete_task(task_id, db)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Không tìm thấy task có ID: {task_id}"
        )
        
    return result

@task_router.patch(
    "/{task_id}",
    response_model=schemas.TaskResponse,
    summary="Cập nhật vài thuộc tính thông tin của nhiệm vụ",
)
async def update_task(
    task_id: Annotated[int, Path()],
    task_data: schemas.TaskUpdate,
    db: DBSession,
    current_user: UPDATE_TASK_PERMISSION
):
    result = await TaskService.update_task(task_data, task_id, db)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Không tìm thấy task có ID: {task_id}"
        )
        
    return result