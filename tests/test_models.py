# tests/test_models.py
"""Unit tests for the database models (without DB interaction initially)."""

# Import only the models needed from your flaskr application
from flaskr.models import User, Skill, UserProgress, QuestionLog

# Removed: import datetime (unused)
# Removed: from sqlalchemy import Column (unused in this file)


def test_user_model_creation():
    """Test creating a User instance."""
    user = User(user_identifier="testuser1")
    assert user.user_identifier == "testuser1"
    # Python-level defaults like created_at/updated_at are typically
    # None until handled by the database via server_default.


def test_skill_model_creation():
    """Test creating a Skill instance."""
    skill = Skill(skill_id_string="test-skill-1", name="Test Skill")
    assert skill.skill_id_string == "test-skill-1"
    assert skill.name == "Test Skill"
    assert skill.description is None


def test_user_progress_model_creation():
    """Test creating a UserProgress instance and default values."""
    # This test relies on the __init__ method or the default= parameter
    # in the UserProgress model definition working correctly.
    progress = UserProgress(user_id=1, skill_id=1)
    # Removed incorrect import: from . import db
    # Removed diagnostic prints

    assert progress.user_id == 1
    assert progress.skill_id == 1
    # Check the defaults are applied during Python object creation
    assert (
        progress.current_difficulty == 2
    ), f"Expected default 2, got {progress.current_difficulty}"
    assert (
        progress.correct_streak == 0
    ), f"Expected default 0, got {progress.correct_streak}"
    assert (
        progress.incorrect_streak == 0
    ), f"Expected default 0, got {progress.incorrect_streak}"
    # This should be None unless explicitly set or defaulted in Python
    assert progress.last_interaction_at is None


def test_question_log_model_creation():
    """Test creating a QuestionLog instance with minimal data."""
    log = QuestionLog(
        user_id=1,
        skill_id=1,
        difficulty_presented=2,
        question_text_generated="Solve 2x = 4",
    )
    assert log.user_id == 1
    assert log.skill_id == 1
    assert log.difficulty_presented == 2
    assert log.question_text_generated == "Solve 2x = 4"
    # Check other fields are None or default if applicable
    assert log.user_answer is None
    assert log.is_correct is None
    assert log.session_id is None  # Assuming no Python default
    assert log.prompt_used is None  # Assuming no Python default
    assert log.expected_answer is None  # Assuming no Python default
    assert log.response_time_ms is None  # Assuming no Python default
    assert log.feedback_given is None  # Assuming no Python default
