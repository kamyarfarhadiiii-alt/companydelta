from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Notification, User
from app.templating import templates

router = APIRouter(prefix="/notifications")


@router.get("/count")
def count(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    unread = Notification.user_id == user.id, Notification.is_read.is_(False)
    n = db.scalar(select(func.count(Notification.id)).where(*unread))
    latest = db.scalar(select(Notification.message).where(*unread).order_by(Notification.id.desc()).limit(1))
    return {"n": n, "latest": latest or ""}


@router.get("")
def page(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.scalars(select(Notification).where(Notification.user_id == user.id)
                       .order_by(Notification.id.desc()).limit(50)).all()
    fresh = {n.id for n in items if not n.is_read}
    resp = templates.TemplateResponse(request, "notifications.html", {"user": user, "items": items, "fresh": fresh})
    for n in items:
        n.is_read = True
    db.commit()
    return resp
