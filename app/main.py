from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app import models  # noqa: F401  (برای شناسایی مدل‌ها)
from app.core.config import settings
from app.database import Base, engine
from app.routers import activities, attendance, auth, notifications, pages, reports, users

app = FastAPI(title=settings.app_name)

# موقت: در مرحله ۱۰ با Alembic جایگزین می‌شود
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(users.router)
app.include_router(activities.router)
app.include_router(notifications.router)
app.include_router(reports.router)
app.include_router(attendance.router)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return RedirectResponse("/login", status_code=303)
    return await http_exception_handler(request, exc)
