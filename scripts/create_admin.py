from getpass import getpass

from sqlalchemy import select

from app import models  # noqa: F401
from app.auth.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Role, User

Base.metadata.create_all(bind=engine)

first = input("نام: ").strip()
last = input("نام خانوادگی: ").strip()
username = input("نام کاربری: ").strip().lower()
password = getpass("رمز عبور (حداقل ۸ کاراکتر): ")

if len(password) < 8:
    raise SystemExit("رمز عبور کوتاه است.")

with SessionLocal() as db:
    if db.scalar(select(User).where(User.username == username)):
        raise SystemExit("این نام کاربری وجود دارد.")
    db.add(User(first_name=first, last_name=last, username=username,
                password_hash=hash_password(password), role=Role.admin))
    db.commit()
    print("Admin ساخته شد.")
