import os from sqlalchemy import select
from app import models from app.auth.security import hash_password from app.database import Base, SessionLocal, engine from app.models import Role, User
Base.metadata.create_all(bind=engine)
first = os.getenv("ADMIN_FIRST_NAME") last = os.getenv("ADMIN_LAST_NAME") username = os.getenv("ADMIN_USERNAME") password = os.getenv("ADMIN_PASSWORD")
if not all([first, last, username, password]): raise SystemExit("Admin environment variables are missing.")
if len(password) < 8: raise SystemExit("Admin password must be at least 8 characters.")
with SessionLocal() as db: existing = db.scalar( select(User).where(User.username == username.strip().lower()) )
if existing:
    print("Admin already exists.")
else:
    db.add(
        User(
            first_name=first,
            last_name=last,
            username=username.strip().lower(),
            password_hash=hash_password(password),
            role=Role.admin,
        )
    )
    db.commit()
    print("Admin created successfully.")