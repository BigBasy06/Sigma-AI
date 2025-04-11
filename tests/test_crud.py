# tests/test_crud.py
"""Integration tests for the CRUD operations using the database."""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError  # For testing constraints

from flaskr import crud
from flaskr.models import User, Skill, UserProgress, QuestionLog

# Tests use the 'session' fixture from conftest.py which provides
# an isolated transaction for each test function.


def test_create_and_get_user(session: Session):
    """Test creating a user and retrieving it."""
    identifier = "crud_user_1"
    user = crud.create_user(session, user_identifier=identifier)
    assert user.id is not None
    assert user.user_identifier == identifier
    assert user.created_at is not None

    retrieved_user = crud.get_user_by_identifier(session, identifier)
    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    assert retrieved_user.user_identifier == identifier

    retrieved_by_id = crud.get_user_by_id(session, user.id)
    assert retrieved_by_id is not None
    assert retrieved_by_id.id == user.id


def test_create_user_duplicate_identifier(session: Session):
    """Test that creating a user with a duplicate identifier fails."""
    identifier = "duplicate_user"
    crud.create_user(session, user_identifier=identifier)  # Create first user

    # Expect an IntegrityError or ValueError depending on implementation
    with pytest.raises((IntegrityError, ValueError)):
        crud.create_user(session, user_identifier=identifier)
    # Ensure session is still usable after expected exception
    session.rollback()  # Important after expected error with commit


def test_create_and_get_skill(session: Session):
    """Test creating a skill and retrieving it."""
    skill_id_str = "linear-crud-test"
    skill_name = "CRUD Linear Test"
    skill = crud.create_skill(session, skill_id_string=skill_id_str, name=skill_name)
    assert skill.id is not None
    assert skill.skill_id_string == skill_id_str
    assert skill.name == skill_name

    retrieved_skill = crud.get_skill_by_id_string(session, skill_id_str)
    assert retrieved_skill is not None
    assert retrieved_skill.id == skill.id
    assert retrieved_skill.name == skill_name


def test_get_or_create_user_progress(session: Session):
    """Test getting or creating user progress records."""
    user = crud.create_user(session, user_identifier="progress_user")
    skill = crud.create_skill(
        session, skill_id_string="progress_skill", name="Progress Skill"
    )

    # First call should create
    progress1 = crud.get_or_create_user_progress(session, user.id, skill.id)
    assert progress1.id is not None
    assert progress1.user_id == user.id
    assert progress1.skill_id == skill.id
    assert progress1.current_difficulty == 2  # Default

    # Second call should retrieve the same record
    progress2 = crud.get_or_create_user_progress(session, user.id, skill.id)
    assert progress2.id == progress1.id

    # Test UniqueConstraint (should implicitly be covered by get_or_create logic)
    # Attempting direct creation might raise IntegrityError if get_or_create wasn't used
    # progress_dup = UserProgress(user_id=user.id, skill_id=skill.id)
    # session.add(progress_dup)
    # with pytest.raises(IntegrityError):
    #     session.commit()
    # session.rollback()


def test_create_question_log(session: Session):
    """Test creating a basic question log entry."""
    user = crud.create_user(session, user_identifier="log_user")
    skill = crud.create_skill(session, skill_id_string="log_skill", name="Log Skill")

    log_data = {
        "user_id": user.id,
        "skill_id": skill.id,
        "difficulty_presented": 3,
        "question_text_generated": "What is 5x if x=3?",
        "expected_answer": "15",
        "user_answer": "15",
        "is_correct": True,
        "response_time_ms": 5000,
    }
    log_entry = crud.create_question_log(session, log_data)
    assert log_entry.id is not None
    assert log_entry.user_id == user.id
    assert log_entry.skill_id == skill.id
    assert log_entry.is_correct is True
    assert log_entry.question_timestamp is not None

    # Test retrieval
    logs = crud.get_recent_logs_for_user_skill(session, user.id, skill.id, limit=1)
    assert len(logs) == 1
    assert logs[0].id == log_entry.id
