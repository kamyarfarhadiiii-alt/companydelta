from datetime import datetime, timezone
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Attendance, Role, User
from app.templating import templates, today_bounds

router = APIRouter(prefix="/attendance")


def open_record(db: Session, user_id: int):
    return db.scalar(select(Attendance).where(
        Attendance.user_id == user_id, Attendance.check_out.is_(None)))


def back(err: str = ""):
    return RedirectResponse("/attendance" + (f"?{urlencode({'err': err})}" if err else ""), status_code=303)


@router.get("")
def page(request: Request, err: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    mine = db.scalars(select(Attendance).where(Attendance.user_id == user.id)
                      .order_by(Attendance.check_in.desc()).limit(30)).all()
    today_all = []
    if user.role == Role.admin:
        start, end = today_bounds()
        today_all = db.scalars(select(Attendance).where(Attendance.check_in >= start, Attendance.check_in < end)
                               .order_by(Attendance.check_in)).all()
    return templates.TemplateResponse(request, "attendance.html", {
        "user": user, "mine": mine, "current": open_record(db, user.id),
        "today_all": today_all, "err": err[:200]})


@router.post("/check-in")
def check_in(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if open_record(db, user.id):
        return back("ورود شما قبلاً ثبت شده است. ابتدا خروج بزنید.")
    db.add(Attendance(user_id=user.id, check_in=datetime.now(timezone.utc)))
    db.commit()
    return back()


@router.post("/check-out")
def check_out(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rec = open_record(db, user.id)
    if not rec:
        return back("ورودی برای ثبت خروج وجود ندارد.")
    rec.check_out = datetime.now(timezone.utc)
    db.commit()
    return back()
