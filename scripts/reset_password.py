from getpass import getpass

from sqlalchemy import select

from app import models  # noqa: F401
from app.auth.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Role, User

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    users = db.scalars(select(User)).all()
    print("Existing users:", [u.username for u in users] or "none")

    username = input("username: ").strip().lower()
    password = getpass("new password (min 8 chars): ")
    if len(password) < 8:
        raise SystemExit("Password too short.")

    user = db.scalar(select(User).where(User.username == username))
    if user:
        user.password_hash = hash_password(password)
        user.is_active = True
        print("Password updated.")
    else:
        db.add(User(first_name="Admin", last_name="User", username=username,
                    password_hash=hash_password(password), role=Role.admin))
        print("New admin created.")
    db.commit()
