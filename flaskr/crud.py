# flaskr/crud.py
"""
Basic CRUD (Create, Read, Update, Delete) operations for SQLAlchemy models.
These functions expect a SQLAlchemy Session object. In a Flask context,
this is typically obtained from the request context or managed by an extension,
and then passed into these functions.
"""
import datetime
from sqlalchemy.orm import Session
from typing import List, Optional

# Import your models (adjust path if needed)
from .models import User, Skill, UserProgress, QuestionLog

# Import 'db' if you need access to db.session within these functions,
# but typically the session is passed in from the Flask request context.
# from . import db  # <-- REMOVED THIS LINE as it was unused

# --- User CRUD ---


def create_user(db_session: Session, user_identifier: str) -> User:
    """Creates a new user. Returns the created user instance."""
    # Check if identifier already exists
    existing_user = get_user_by_identifier(db_session, user_identifier)
    if existing_user:
        raise ValueError(f"User identifier '{user_identifier}' already exists.")

    new_user = User(user_identifier=user_identifier)
    db_session.add(new_user)
    # Commit should ideally happen at the end of a request lifecycle in Flask
    # For standalone use or clarity, commit can be here. Let's assume it is.
    db_session.commit()
    db_session.refresh(new_user)  # Refresh to get ID and defaults like created_at
    return new_user


def get_user_by_id(db_session: Session, user_id: int) -> Optional[User]:
    """Gets a user by their primary key ID."""
    # Use session.get for efficient PK lookups (introduced in SQLAlchemy 1.4)
    return db_session.get(User, user_id)


def get_user_by_identifier(db_session: Session, identifier: str) -> Optional[User]:
    """Gets a user by their unique identifier string."""
    return db_session.query(User).filter(User.user_identifier == identifier).first()


def update_user_identifier(
    db_session: Session, user_id: int, new_identifier: str
) -> Optional[User]:
    """Updates a user's identifier. Returns updated user or None if not found."""
    user = get_user_by_id(db_session, user_id)
    if user:
        # Check for potential identifier conflict before updating
        existing = get_user_by_identifier(db_session, new_identifier)
        if existing and existing.id != user_id:
            raise ValueError(
                f"Identifier '{new_identifier}' is already in use by another user."
            )
        user.user_identifier = new_identifier
        # updated_at is handled by onupdate=func.now() in the model
        db_session.commit()
        db_session.refresh(user)
    return user


def delete_user(db_session: Session, user_id: int) -> bool:
    """Deletes a user by ID. Returns True if deleted, False otherwise."""
    user = get_user_by_id(db_session, user_id)
    if user:
        db_session.delete(user)
        db_session.commit()
        return True
    return False


# --- Skill CRUD ---


def create_skill(
    db_session: Session,
    skill_id_string: str,
    name: str,
    description: Optional[str] = None,
) -> Skill:
    """Creates a new skill. Returns the created skill instance."""
    existing_skill = get_skill_by_id_string(db_session, skill_id_string)
    if existing_skill:
        raise ValueError(f"Skill ID string '{skill_id_string}' already exists.")

    new_skill = Skill(
        skill_id_string=skill_id_string, name=name, description=description
    )
    db_session.add(new_skill)
    db_session.commit()
    db_session.refresh(new_skill)
    return new_skill


def get_skill_by_id(db_session: Session, skill_id: int) -> Optional[Skill]:
    """Gets a skill by its primary key ID."""
    return db_session.get(Skill, skill_id)


def get_skill_by_id_string(db_session: Session, skill_id_str: str) -> Optional[Skill]:
    """Gets a skill by its unique string identifier."""
    return db_session.query(Skill).filter(Skill.skill_id_string == skill_id_str).first()


def get_all_skills(db_session: Session) -> List[Skill]:
    """Gets all skills."""
    return db_session.query(Skill).order_by(Skill.name).all()


# Add update_skill, delete_skill as needed

# --- UserProgress CRUD ---


def get_user_progress(
    db_session: Session, user_id: int, skill_id: int
) -> Optional[UserProgress]:
    """Gets the progress record for a specific user and skill."""
    return (
        db_session.query(UserProgress)
        .filter_by(user_id=user_id, skill_id=skill_id)
        .first()
    )


def get_or_create_user_progress(
    db_session: Session, user_id: int, skill_id: int, default_difficulty: int = 2
) -> UserProgress:
    """Gets existing progress or creates a new record for a user/skill."""
    progress = get_user_progress(db_session, user_id, skill_id)
    if not progress:
        # Ensure user and skill exist before creating progress
        user = get_user_by_id(db_session, user_id)
        skill = get_skill_by_id(db_session, skill_id)
        if not user:
            raise ValueError(f"User with id={user_id} does not exist.")
        if not skill:
            raise ValueError(f"Skill with id={skill_id} does not exist.")

        print(
            f"Creating new progress for user {user_id}, skill {skill_id}"
        )  # Debug log
        progress = UserProgress(
            user_id=user_id,
            skill_id=skill_id,
            current_difficulty=default_difficulty,
            # Streaks default to 0 per model definition
        )
        db_session.add(progress)
        db_session.commit()
        db_session.refresh(progress)
    return progress


def update_user_progress_state(
    db_session: Session,
    user_id: int,
    skill_id: int,
    difficulty: Optional[int] = None,
    correct_streak: Optional[int] = None,
    incorrect_streak: Optional[int] = None,
) -> Optional[UserProgress]:
    """Updates specific adaptive state fields of a UserProgress record."""
    progress = get_user_progress(db_session, user_id, skill_id)
    if progress:
        updated = False
        if difficulty is not None:
            progress.current_difficulty = difficulty
            updated = True
        if correct_streak is not None:
            progress.correct_streak = correct_streak
            updated = True
        if incorrect_streak is not None:
            progress.incorrect_streak = incorrect_streak
            updated = True

        if updated:
            progress.last_interaction_at = datetime.datetime.now(
                datetime.timezone.utc
            )  # Use timezone-aware UTC now  # Update interaction time
            db_session.commit()
            db_session.refresh(progress)
    return progress


# --- QuestionLog CRUD ---


def create_question_log(db_session: Session, log_data: dict) -> QuestionLog:
    """
    Creates a new question log entry.
    Expects a dictionary with keys matching QuestionLog model fields.
    Performs basic validation for required foreign keys.
    """
    required_fk_fields = ["user_id", "skill_id"]
    if not all(field in log_data for field in required_fk_fields):
        raise ValueError("Missing required user_id or skill_id for QuestionLog.")

    # Optional: Basic check if user/skill exist can be added here if needed,
    # but foreign key constraints should typically handle this.
    # user = get_user_by_id(db_session, log_data["user_id"])
    # skill = get_skill_by_id(db_session, log_data["skill_id"])
    # if not user or not skill:
    #     raise ValueError("User or Skill referenced in log does not exist.")

    new_log = QuestionLog(**log_data)
    db_session.add(new_log)
    db_session.commit()
    db_session.refresh(new_log)
    return new_log


def get_recent_logs_for_user_skill(
    db_session: Session, user_id: int, skill_id: int, limit: int = 10
) -> List[QuestionLog]:
    """Gets the most recent logs for a specific user and skill."""
    return (
        db_session.query(QuestionLog)
        .filter_by(user_id=user_id, skill_id=skill_id)
        .order_by(QuestionLog.question_timestamp.desc())
        .limit(limit)
        .all()
    )


# Add other specific query functions as needed
