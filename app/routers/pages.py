from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Activity, Attendance, Role, Status, User
from app.templating import templates, today_bounds

router = APIRouter()


@router.get("/")
def index():
    return RedirectResponse("/dashboard")


@router.get("/dashboard")
def dashboard(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    start, end = today_bounds()
    today = Attendance.check_in >= start, Attendance.check_in < end
    staff = db.scalar(select(func.count(User.id)).where(User.is_active, User.role != Role.admin))
    present = db.scalar(select(func.count(func.distinct(Attendance.user_id))).join(User, User.id == Attendance.user_id)
                        .where(User.role != Role.admin, *today))

    def acts(status):
        q = select(func.count(Activity.id)).where(Activity.status == status)
        if user.role == Role.secretary:
            q = q.where(Activity.user_id == user.id)
        return db.scalar(q)

    stats = {
        "staff": staff, "present": present, "absent": max(staff - present, 0),
        "entries": db.scalar(select(func.count(Attendance.id)).where(*today)),
        "inside": db.scalar(select(func.count(Attendance.id)).where(Attendance.check_out.is_(None))),
        "pending": acts(Status.pending), "approved": acts(Status.approved), "rejected": acts(Status.rejected),
        "mine_in": db.scalar(select(func.count(Attendance.id)).where(Attendance.user_id == user.id,
                                                                    Attendance.check_out.is_(None))),
    }
    return templates.TemplateResponse(request, "dashboard.html", {"user": user, "stats": stats})
