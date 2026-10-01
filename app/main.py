from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.projects.router import project_router, task_router
from app.core.dependencies import create_admin, load_permissions

@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_permissions()    # Khởi tạo permissions trong cơ sở dữ liệu nếu chưa tồn tại
    await create_admin()        # Khởi tạo Admin User trong cơ sở dữ liệu nếu chưa tồn tại
    
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)
    
# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://project-manager-frontend-blush.vercel.app/login"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(project_router)
app.include_router(task_router)