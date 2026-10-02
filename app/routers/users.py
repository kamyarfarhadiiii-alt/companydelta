import re
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.auth.security import hash_password
from app.database import get_db
from app.models import Role, User
from app.templating import templates

router = APIRouter(prefix="/users")
admin_only = require_roles(Role.admin)
USERNAME_RE = re.compile(r"^[a-z0-9_.]{3,50}$")


def back(msg: str = "", err: str = ""):
    q = urlencode({k: v for k, v in (("msg", msg), ("err", err)) if v})
    return RedirectResponse(f"/users?{q}", status_code=303)


@router.get("")
def list_users(request: Request, msg: str = "", err: str = "",
               user: User = Depends(admin_only), db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.id)).all()
    return templates.TemplateResponse(
        request, "users.html", {"user": user, "users": users, "msg": msg[:200], "err": err[:200]})


@router.post("/create")
def create_user(first_name: str = Form(..., max_length=100), last_name: str = Form(..., max_length=100),
                username: str = Form(..., max_length=50), password: str = Form(..., max_length=72),
                role: str = Form(...), user: User = Depends(admin_only), db: Session = Depends(get_db)):
    username = username.strip().lower()
    if not first_name.strip() or not last_name.strip():
        return back(err="نام و نام خانوادگی الزامی است.")
    if not USERNAME_RE.match(username):
        return back(err="نام کاربری باید انگلیسی و ۳ تا ۵۰ کاراکتر (حرف، عدد، _ یا .) باشد.")
    if len(password) < 8:
        return back(err="رمز عبور باید حداقل ۸ کاراکتر باشد.")
    try:
        role_enum = Role(role)
    except ValueError:
        return back(err="نقش نامعتبر است.")
    if db.scalar(select(User).where(User.username == username)):
        return back(err="این نام کاربری قبلاً ثبت شده است.")
    db.add(User(first_name=first_name.strip(), last_name=last_name.strip(), username=username,
                password_hash=hash_password(password), role=role_enum))
    db.commit()
    return back(msg="کاربر جدید ساخته شد.")


@router.post("/{user_id}/update")
def update_user(user_id: int, first_name: str = Form(..., max_length=100), last_name: str = Form(..., max_length=100),
                role: str = Form(...), is_active: str = Form(""), password: str = Form("", max_length=72),
                user: User = Depends(admin_only), db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        return back(err="کاربر پیدا نشد.")
    try:
        role_enum = Role(role)
    except ValueError:
        return back(err="نقش نامعتبر است.")
    active = is_active == "on"
    if target.id == user.id and (not active or role_enum != Role.admin):
        return back(err="نمی‌توانید حساب یا نقش خودتان را تنزل دهید.")
    if password and len(password) < 8:
        return back(err="رمز جدید باید حداقل ۸ کاراکتر باشد.")
    target.first_name, target.last_name = first_name.strip(), last_name.strip()
    target.role, target.is_active = role_enum, active
    if password:
        target.password_hash = hash_password(password)
    db.commit()
    return back(msg="تغییرات ذخیره شد.")
