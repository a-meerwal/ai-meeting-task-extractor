from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    transcript: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="processing", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # cascade="all, delete-orphan" ensures tasks are deleted if a meeting is deleted
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="meeting", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # Indexing foreign keys is a Postgres best practice for JOIN performance
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"), index=True)
    task_description: Mapped[str] = mapped_column(Text)
    assignee: Mapped[str] = mapped_column(String(255), nullable=True)
    deadline: Mapped[str] = mapped_column(String(255), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="tasks")
