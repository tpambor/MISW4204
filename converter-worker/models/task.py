import datetime
from enum import IntEnum
import db
from sqlalchemy import String, DateTime, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

class TaskStatus(IntEnum):
    UPLOADED = 1
    PROCESSED = 2

class Task(db.Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    created: Mapped[datetime.datetime] = mapped_column(DateTime(), nullable=False)
    status: Mapped[int] = mapped_column(Integer(), nullable=False)
    fileName: Mapped[str] = mapped_column(String(), nullable=False)
    oldFormat: Mapped[str] = mapped_column(String(), nullable=False)
    newFormat: Mapped[str] = mapped_column(String(), nullable=False)
    finished: Mapped[datetime.datetime] = mapped_column(DateTime())
