from sqlalchemy.orm import Session

from app.models import Notification


def notify(db: Session, user_id: int, message: str, link: str = "") -> None:
    """اعلان می‌سازد؛ commit توسط فراخواننده انجام می‌شود."""
    db.add(Notification(user_id=user_id, message=message[:255], link=link))
