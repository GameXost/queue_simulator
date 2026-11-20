import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Role(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"


class EntryStatus(str, enum.Enum):
    waiting = "waiting"
    checking = "checking"
    passed = "passed"
    failed = "failed"
    postponed = "postponed"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320), unique=True)
    group_name: Mapped[str | None] = mapped_column(String(50))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role, name="user_role"), default=Role.student)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sessions: Mapped[list["QueueSession"]] = relationship(back_populates="teacher")

    @property
    def can_teach(self) -> bool:
        return self.role in (Role.teacher, Role.admin)


class QueueSession(Base):
    __tablename__ = "queue_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    minutes_per_student: Mapped[int] = mapped_column(Integer)
    at_risk_minutes: Mapped[int] = mapped_column(Integer, default=20)
    code: Mapped[str] = mapped_column(String(16), unique=True)
    is_open: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    teacher: Mapped[User] = relationship(back_populates="sessions")
    entries: Mapped[list["QueueEntry"]] = relationship(back_populates="session")


class QueueEntry(Base):
    __tablename__ = "queue_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("queue_sessions.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    work_title: Mapped[str] = mapped_column(String(100))
    status: Mapped[EntryStatus] = mapped_column(Enum(EntryStatus, name="entry_status"), default=EntryStatus.waiting)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    session: Mapped[QueueSession] = relationship(back_populates="entries")
    user: Mapped[User] = relationship()
