# flaskr/models.py
"""
Database model definitions for the Sigma AI Flask application.
Uses Flask-SQLAlchemy ORM.
"""
import datetime
from typing import Optional, List  # Removed TYPE_CHECKING, cast

from sqlalchemy import (
    String,
    Integer,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    Index,
    text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    DeclarativeBase,  # Added for Base class
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Import the db instance created in __init__.py
from . import db


# Base class for declarative models (optional but good practice)
class Base(DeclarativeBase):
    pass


# Modified User class using db.Model
class User(db.Model, UserMixin):  # type: ignore[name-defined]
    """Represents a user in the application."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_identifier: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    # Store hashed passwords, never plain text!
    # Start Non-null. If other auth methods are added later, consider making nullable.
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    progress: Mapped[List["UserProgress"]] = relationship(
        "UserProgress", back_populates="user", cascade="all, delete-orphan"
    )
    logs: Mapped[List["QuestionLog"]] = relationship(
        "QuestionLog", back_populates="user", cascade="all, delete-orphan"
    )

    # Password handling methods
    def set_password(self, password: str) -> None:
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Checks if the provided password matches the stored hash."""
        # Since password_hash is non-nullable, we don't need the None check
        return check_password_hash(self.password_hash, password)

    # __repr__
    def __repr__(self) -> str:
        """Provide a helpful representation when printing the object."""
        return f"<User id={self.id}, identifier='{self.user_identifier}'>"


# Skill Class using db.Model
class Skill(db.Model):  # type: ignore[name-defined]
    """Represents a skill that users can practice."""

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    skill_id_string: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    # Relationships
    user_progress: Mapped[List["UserProgress"]] = relationship(
        "UserProgress", back_populates="skill", cascade="all, delete-orphan"
    )
    logs: Mapped[List["QuestionLog"]] = relationship(
        "QuestionLog", back_populates="skill"
    )

    def __repr__(self) -> str:
        """Provide a helpful representation when printing the object."""
        return (
            f"<Skill id={self.id}, "
            f"skill_id='{self.skill_id_string}', name='{self.name}'>"
        )


# UserProgress Class using db.Model
class UserProgress(db.Model):  # type: ignore[name-defined]
    """
    Tracks a user's progress and difficulty level for a specific skill.
    """

    __tablename__ = "user_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),
        Index("ix_user_progress_user_skill", "user_id", "skill_id"),
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(ForeignKey("users.id"), nullable=False)
    skill_id = db.Column(ForeignKey("skills.id"), nullable=False)
    current_difficulty = db.Column(Integer, nullable=False, default=2)
    correct_streak = db.Column(Integer, nullable=False, default=0)
    incorrect_streak = db.Column(Integer, nullable=False, default=0)
    last_interaction_at = db.Column(DateTime, nullable=True)

    # Timestamps using mapped_column
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    def __init__(self, **kwargs):
        kwargs["current_difficulty"] = kwargs.get("current_difficulty", 2)
        kwargs["correct_streak"] = kwargs.get("correct_streak", 0)
        kwargs["incorrect_streak"] = kwargs.get("incorrect_streak", 0)
        super().__init__(**kwargs)

    # Relationships
    user = relationship("User", back_populates="progress")
    skill = relationship("Skill", back_populates="user_progress")

    def __repr__(self) -> str:
        """Provide a helpful representation when printing the object."""
        return (
            f"<UserProgress user={self.user_id}, skill={self.skill_id},"
            f" difficulty={self.current_difficulty}>"
        )


# QuestionLog Class using db.Model
class QuestionLog(db.Model):  # type: ignore[name-defined]
    """Logs each question presented to a user and their response."""

    __tablename__ = "question_logs"
    __table_args__ = (
        Index(
            "ix_question_logs_user_skill_time",
            "user_id",
            "skill_id",
            "question_timestamp",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id"), nullable=False, index=True
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True
    )
    question_timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
    )
    difficulty_presented: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    question_text_generated: Mapped[str] = mapped_column(Text, nullable=False)
    expected_answer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_answer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    feedback_given: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="logs")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="logs")

    def __repr__(self) -> str:
        """Provide a helpful representation when printing the object."""
        is_correct = self.is_correct
        correct_str = (
            f"correct={is_correct}" if is_correct is not None else "unanswered"
        )
        return (
            f"<Log id={self.id}, user={self.user_id}, "
            f"skill={self.skill_id}, {correct_str}>"
        )
