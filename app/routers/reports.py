from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models import Attendance, Role, User
from app.templating import TZ, jdate, local, templates, to_gregorian

router = APIRouter(prefix="/reports")


def parse_j(text: str) -> date:
    text = text.strip().translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")).replace("-", "/")
    y, m, d = (int(x) for x in text.split("/"))
    if not (1 <= m <= 12 and 1 <= d <= 31):
        raise ValueError
    return date(*to_gregorian(y, m, d))


@router.get("")
def attendance_report(request: Request, user_id: int = 0, date_from: str = "", date_to: str = "",
                      user: User = Depends(require_roles(Role.admin)), db: Session = Depends(get_db)):
    now = datetime.now(TZ)
    err, rows, records = "", [], []
    date_to = date_to or jdate(now)
    date_from = date_from or date_to[:-2] + "01"
    staff = db.scalars(select(User).where(User.role != Role.admin).order_by(User.first_name)).all()
    try:
        d1, d2 = parse_j(date_from), parse_j(date_to)
        if d2 < d1 or (d2 - d1).days > 93:
            raise ValueError
    except ValueError:
        err = "تاریخ‌ها را به شکل 1405/07/01 و حداکثر ۹۳ روز وارد کنید."
    if not err:
        start = datetime(d1.year, d1.month, d1.day, tzinfo=TZ).astimezone(timezone.utc)
        end = (datetime(d2.year, d2.month, d2.day, tzinfo=TZ) + timedelta(days=1)).astimezone(timezone.utc)
        q = select(Attendance).where(Attendance.check_in >= start, Attendance.check_in < end).order_by(Attendance.check_in)
        if user_id:
            q = q.where(Attendance.user_id == user_id)
        records = [r for r in db.scalars(q).all() if r.user.role != Role.admin]
        last = min(d2, now.date())
        workdays = [d1 + timedelta(days=i) for i in range((last - d1).days + 1) if (d1 + timedelta(days=i)).weekday() != 4]
        for u in staff:
            if user_id and u.id != user_id:
                continue
            mine = [r for r in records if r.user_id == u.id]
            days = {local(r.check_in).date() for r in mine}
            mins = sum(int((local(r.check_out) - local(r.check_in)).total_seconds()) // 60 for r in mine if r.check_out)
            rows.append({"user": u, "days": len(days), "time": f"{mins // 60} ساعت و {mins % 60} دقیقه",
                         "absent": len([d for d in workdays if d not in days])})
    return templates.TemplateResponse(request, "reports.html", {
        "user": user, "staff": staff, "rows": rows, "records": records, "err": err,
        "user_id": user_id, "date_from": date_from, "date_to": date_to})
