"""Очередь: запись, выход, отметки преподавателя, таблица с прогнозом.
Каждая функция, меняющая очередь, после commit вызывает realtime.notify_changed(code)."""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import EntryStatus, QueueEntry, QueueSession, User
from app.services.forecast import Slot, build_forecast


def join(db: Session, session: QueueSession, user: User, work_title: str) -> QueueEntry:
    raise NotImplementedError


def leave(db: Session, session: QueueSession, user: User) -> None:
    raise NotImplementedError


def start_check(db: Session, entry: QueueEntry) -> None:
    raise NotImplementedError


def finish(db: Session, entry: QueueEntry, status: EntryStatus) -> None:
    """status: passed / failed / postponed."""
    raise NotImplementedError


def table(db: Session, session: QueueSession, now: datetime) -> list[tuple[QueueEntry, Slot | None]]:
    """Записи сдачи в порядке очереди; у завершённых Slot = None."""
    query = (
        select(QueueEntry)
        .where(QueueEntry.session_id == session.id, QueueEntry.status != EntryStatus.cancelled)
        .options(selectinload(QueueEntry.user))
    )
    entries = list(db.scalars(query))
    by_id = {e.id: e for e in entries}
    slots = build_forecast(session, entries, now)
    in_queue = {s.entry_id for s in slots}
    done = sorted((e for e in entries if e.id not in in_queue), key=lambda e: e.finished_at or e.joined_at)
    return [(by_id[s.entry_id], s) for s in slots] + [(e, None) for e in done]
