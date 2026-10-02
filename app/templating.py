from datetime import datetime, timedelta, timezone

from fastapi.templating import Jinja2Templates

TZ = timezone(timedelta(hours=3, minutes=30))  # ایران (بدون ساعت تابستانی)


def local(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TZ)


def to_jalali(gy: int, gm: int, gd: int):
    g = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = (355666 + 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100
            + (gy2 + 399) // 400 + gd + g[gm - 1])
    jy = -1595 + 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm, jd = 1 + days // 31, 1 + days % 31
    else:
        jm, jd = 7 + (days - 186) // 30, 1 + (days - 186) % 30
    return jy, jm, jd


def to_gregorian(jy: int, jm: int, jd: int):
    jy += 1595
    days = (-355668 + 365 * jy + (jy // 33) * 8 + ((jy % 33) + 3) // 4 + jd
            + ((jm - 1) * 31 if jm < 7 else (jm - 7) * 30 + 186))
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    leap = (gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0
    months = [0, 31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 0
    while gm < 13 and gd > months[gm]:
        gd -= months[gm]
        gm += 1
    return gy, gm, gd


def jdate(dt: datetime) -> str:
    l = local(dt)
    y, m, d = to_jalali(l.year, l.month, l.day)
    return f"{y}/{m:02d}/{d:02d}"


def jtime(dt: datetime | None) -> str:
    return local(dt).strftime("%H:%M") if dt else "—"


def duration(a: datetime, b: datetime | None) -> str:
    if not b:
        return "—"
    mins = int((local(b) - local(a)).total_seconds()) // 60
    return f"{mins // 60} ساعت و {mins % 60} دقیقه"


def today_bounds():
    now = datetime.now(TZ)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start.astimezone(timezone.utc), (start + timedelta(days=1)).astimezone(timezone.utc)


STATUS_FA = {'pending': 'در انتظار بررسی', 'approved': 'تأیید شده', 'rejected': 'رد شده'}
STATUS_CLS = {'pending': 'y', 'approved': 'g', 'rejected': 'r'}

templates = Jinja2Templates(directory="app/templates")
templates.env.filters.update(jdate=jdate, jtime=jtime)
templates.env.globals["duration"] = duration
templates.env.globals.update(STATUS_FA=STATUS_FA, STATUS_CLS=STATUS_CLS)
