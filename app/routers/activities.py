from datetime import datetime, timezone
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models import Activity, Role, Status, User
from app.services.notify import notify
from app.templating import templates

router = APIRouter(prefix="/activities")
staff = require_roles(Role.admin, Role.secretary)


def back(msg: str = "", err: str = ""):
    q = urlencode({k: v for k, v in (("msg", msg), ("err", err)) if v})
    return RedirectResponse(f"/activities?{q}", status_code=303)


@router.get("")
def page(request: Request, status: str = "", msg: str = "", err: str = "",
         user: User = Depends(staff), db: Session = Depends(get_db)):
    q = select(Activity).order_by(Activity.created_at.desc()).limit(100)
    if user.role == Role.secretary:
        q = q.where(Activity.user_id == user.id)
    elif status in Status.__members__:
        q = q.where(Activity.status == Status(status))
    return templates.TemplateResponse(request, "activities.html", {
        "user": user, "items": db.scalars(q).all(), "status": status, "msg": msg[:200], "err": err[:200]})


@router.post("/create")
def create(title: str = Form(..., max_length=200), description: str = Form("", max_length=2000),
           user: User = Depends(require_roles(Role.secretary)), db: Session = Depends(get_db)):
    if not title.strip():
        return back(err="عنوان فعالیت الزامی است.")
    db.add(Activity(user_id=user.id, title=title.strip(), description=description.strip()))
    for admin in db.scalars(select(User).where(User.role == Role.admin, User.is_active)):
        notify(db, admin.id, f"فعالیت جدید توسط {user.full_name} ثبت شد.", "/activities?status=pending")
    db.commit()
    return back(msg="فعالیت ثبت و برای مدیر ارسال شد.")


@router.post("/{activity_id}/review")
def review(activity_id: int, decision: str = Form(...), comment: str = Form("", max_length=500),
           user: User = Depends(require_roles(Role.admin)), db: Session = Depends(get_db)):
    act = db.get(Activity, activity_id)
    if not act or act.status != Status.pending:
        return back(err="این فعالیت پیدا نشد یا قبلاً بررسی شده است.")
    if decision not in ("approved", "rejected"):
        return back(err="تصمیم نامعتبر است.")
    if decision == "rejected" and not comment.strip():
        return back(err="برای رد کردن، توضیح بنویسید.")
    act.status = Status(decision)
    act.admin_comment = comment.strip() or None
    act.reviewed_at = datetime.now(timezone.utc)
    word = "تأیید" if decision == "approved" else "رد"
    notify(db, act.user_id, f"فعالیت «{act.title}» توسط مدیر {word} شد.", "/activities")
    db.commit()
    return back(msg=f"فعالیت {word} شد.")
