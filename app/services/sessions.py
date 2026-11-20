"""Сдачи: создание, поиск по коду, закрытие."""
import secrets
from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import TZ
from app.models import QueueSession, User

PAIRS = {
    1: (time(9, 0), time(10, 30)),
    2: (time(10, 45), time(12, 15)),
    3: (time(13, 0), time(14, 30)),
    4: (time(14, 45), time(16, 15)),
    5: (time(16, 30), time(18, 0)),
    6: (time(18, 15), time(19, 45)),
    7: (time(20, 0), time(21, 30)),
}
CODE_ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"
CODE_LENGTH = 6


def pair_bounds(day: date, pair: int) -> tuple[datetime, datetime]:
    if pair not in PAIRS:
        raise ValueError("Нет такой пары")
    start, end = PAIRS[pair]
    return datetime.combine(day, start, TZ), datetime.combine(day, end, TZ)


def new_code(db: Session) -> str:
    while True:
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
        if get_by_code(db, code) is None:
            return code


def create_session(
    db: Session,
    teacher: User,
    title: str,
    starts_at: datetime,
    ends_at: datetime,
    minutes_per_student: int,
) -> QueueSession:
    title = title.strip()
    if not title:
        raise ValueError("Укажите название сдачи")
    if not 1 <= minutes_per_student <= 90:
        raise ValueError("Минут на студента — от 1 до 90")
    session = QueueSession(
        teacher=teacher,
        title=title,
        starts_at=starts_at,
        ends_at=ends_at,
        minutes_per_student=minutes_per_student,
        at_risk_minutes=20,
        code=new_code(db),
    )
    db.add(session)
    db.commit()
    return session


def get_by_code(db: Session, code: str) -> QueueSession | None:
    return db.scalar(select(QueueSession).where(QueueSession.code == code))


def get_for_teacher(db: Session, teacher: User, session_id: int) -> QueueSession | None:
    session = db.get(QueueSession, session_id)
    return session if session and session.teacher_id == teacher.id else None


def list_for_teacher(db: Session, teacher: User) -> list[QueueSession]:
    query = select(QueueSession).where(QueueSession.teacher_id == teacher.id).order_by(QueueSession.starts_at.desc())
    return list(db.scalars(query))


def close_session(db: Session, session: QueueSession) -> None:
    raise NotImplementedError
