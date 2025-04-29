from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from user_auth.auth import (
    login_user_by_credentials,
    logout_current_user,
    register_user,
    update_user_activity,
)

from app4 import app as flask_app


@pytest.fixture
def app():
    yield flask_app


# ==== Тести для register_user ====
def test_register_user_success(app):
    """Успішна реєстрація нового користувача"""
    with app.app_context():
        mock_user = None
        mock_new_user = MagicMock(id=1)
        mock_playlist = MagicMock()

        with patch("user_auth.auth.User") as MockUser, patch("user_auth.auth.User.query.filter_by") as mock_filter_by, patch("user_auth.auth.db.session") as mock_session, patch("user_auth.auth.Playlist", return_value=mock_playlist), patch("user_auth.auth.login_user") as mock_login:

            # Імітуємо, що користувача з таким email ще нема
            mock_filter_by.return_value.first.return_value = None

            # Імітуємо створення користувача
            MockUser.return_value = mock_new_user

            # Виклик функції
            result, msg = register_user("new@example.com", "password", "TestName")

            assert result is True
            assert "успішна" in msg.lower()
            mock_session.add.assert_any_call(mock_new_user)
            mock_session.add.assert_any_call(mock_playlist)
            assert mock_session.commit.call_count == 2
            mock_login.assert_called_once_with(mock_new_user)


def test_register_user_duplicate(app):
    """Спроба реєстрації з уже існуючим email"""
    with app.app_context():
        mock_user = MagicMock()

        with patch("user_auth.auth.User.query") as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_user

            result, msg = register_user("existing@example.com", "pass", "TestName")
            assert result is False
            assert "вже існує" in msg.lower()


def test_register_user_db_error(app):
    """Помилка під час запису в базу"""
    with app.app_context():
        mock_user = None
        with patch("user_auth.auth.User.query") as mock_query, patch("user_auth.auth.db.session") as mock_session, patch("user_auth.auth.User") as MockUser, patch("user_auth.auth.Playlist"), patch("user_auth.auth.login_user"):

            mock_query.filter_by.return_value.first.return_value = mock_user
            mock_session.commit.side_effect = Exception("DB error")

            result, msg = register_user("test@example.com", "pass", "TestUser")
            assert result is False
            assert "користувач з таким email вже існує!" in msg.lower()


def test_register_user_empty_email(app):
    """Спроба реєстрації з порожнім email"""
    with app.app_context():
        result, msg = register_user("", "pass", "TestUser")
        assert result is False
        assert "існує" in msg.lower() or "помилка" in msg.lower()


def test_register_user_user_creation_exception(app):
    """Виняток під час створення об'єкта User"""
    with app.app_context():
        with patch("user_auth.auth.User.query.filter_by") as mock_filter_by, patch("user_auth.auth.User", side_effect=Exception("creation error")):
            mock_filter_by.return_value.first.return_value = None
            result, msg = register_user("test@example.com", "pass", "TestUser")
            assert result is False
            assert "користувач з таким email вже існує!" in msg.lower()


def test_register_user_playlist_creation_exception(app):
    """Помилка при створенні плейліста"""
    with app.app_context():
        with patch("user_auth.auth.User.query") as mock_query, patch("user_auth.auth.db.session") as mock_session, patch("user_auth.auth.User", return_value=MagicMock(id=1)) as MockUser, patch("user_auth.auth.Playlist", side_effect=Exception("Playlist error")), patch("user_auth.auth.login_user"):

            mock_query.filter_by.return_value.first.return_value = None
            result, msg = register_user("test2@example.com", "pass", "UserX")
            assert result is False
            assert "користувач з таким email вже існує!" in msg.lower()


# ==== Тести для login_user_by_credentials ====
def test_login_user_success(app):
    """Успішний вхід користувача"""
    with app.app_context():
        mock_user = MagicMock()
        mock_user.check_password.return_value = True

        with patch("user_auth.auth.User.query") as mock_query, patch("user_auth.auth.db.session") as mock_session, patch("user_auth.auth.login_user"):

            mock_query.filter_by.return_value.first.return_value = mock_user
            result, msg = login_user_by_credentials("test@example.com", "password")

            assert result is True
            assert "успішно" in msg.lower()
            mock_session.commit.assert_called()


def test_login_user_invalid_password(app):
    """Неправильний пароль"""
    with app.app_context():
        mock_user = MagicMock()
        mock_user.check_password.return_value = False

        with patch("user_auth.auth.User.query") as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_user
            result, msg = login_user_by_credentials("test@example.com", "wrong")
            assert result is False
            assert "неправильний" in msg.lower()


def test_login_user_not_found(app):
    """Користувач не знайдений"""
    with app.app_context():
        with patch("user_auth.auth.User.query") as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            result, msg = login_user_by_credentials("notfound@example.com", "pass")
            assert result is False
            assert "неправильний" in msg.lower()


def test_login_user_empty_email(app):
    """Вхід з порожнім email"""
    with app.app_context():
        result, msg = login_user_by_credentials("", "somepass")
        assert not result
        assert "неправильний" in msg.lower()


def test_login_user_check_password_exception(app):
    """Вхід з неправильним паролем"""
    with app.app_context():
        mock_user = MagicMock()
        mock_user.check_password.side_effect = Exception("boom")
        with patch("user_auth.auth.User.query.filter_by") as mock_query:
            mock_query.return_value.first.return_value = mock_user
            result, msg = login_user_by_credentials("test@example.com", "password")
            assert result is False
            assert "неправильний" in msg.lower()


# ==== Тести для logout_current_user ====
def test_logout_current_user_authenticated(app):
    """Вихід авторизованого користувача"""
    with app.app_context():
        mock_user = MagicMock(is_authenticated=True)
        with patch("user_auth.auth.update_user_activity") as mock_update, patch("user_auth.auth.db.session") as mock_session, patch("user_auth.auth.logout_user"):

            msg = logout_current_user(mock_user)
            assert "вийшли" in msg.lower()
            mock_update.assert_called_once()
            mock_session.commit.assert_called_once()


def test_logout_current_user_not_authenticated(app):
    """Вихід неавторизованого користувача"""
    with app.app_context():
        mock_user = MagicMock(is_authenticated=False)
        with patch("user_auth.auth.logout_user") as mock_logout:
            msg = logout_current_user(mock_user)
            assert "вийшли" in msg.lower()
            mock_logout.assert_called_once()


# ==== Тести для update_user_activity ====
def test_update_user_activity_active(app):
    """Оновлення часу для активного користувача"""
    with app.app_context():
        now = datetime.utcnow()
        mock_user = MagicMock(is_authenticated=True, last_active=now - timedelta(seconds=60), total_time_online=10)

        with patch("user_auth.auth.db.session") as mock_session:
            update_user_activity(mock_user)

            assert mock_user.total_time_online > 10
            assert mock_user.last_active >= now
            mock_session.commit.assert_called_once()


def test_update_user_activity_too_old(app):
    """Відкидається занадто старе оновлення (>3 хв)"""
    with app.app_context():
        now = datetime.utcnow()
        mock_user = MagicMock(is_authenticated=True, last_active=now - timedelta(minutes=10), total_time_online=100)

        with patch("user_auth.auth.db.session") as mock_session:
            update_user_activity(mock_user)

            assert mock_user.total_time_online == 100
            mock_session.commit.assert_called_once()


def test_update_user_activity_no_last_active(app):
    """Встановлюється last_active, якщо його не було"""
    with app.app_context():
        now = datetime.utcnow()
        mock_user = MagicMock(is_authenticated=True, last_active=None, total_time_online=0)

        with patch("user_auth.auth.db.session") as mock_session:
            update_user_activity(mock_user)

            assert mock_user.last_active >= now
            assert mock_user.total_time_online == 0
            mock_session.commit.assert_called_once()


def test_update_user_activity_not_authenticated(app):
    """Не виконується оновлення, якщо користувач неавторизований"""
    with app.app_context():
        mock_user = MagicMock(is_authenticated=False)

        with patch("user_auth.auth.db.session") as mock_session:
            update_user_activity(mock_user)

            mock_session.commit.assert_not_called()


def test_update_user_activity_invalid_last_active(app):
    """last_active не є datetime"""
    with app.app_context():
        mock_user = MagicMock(is_authenticated=True, last_active="not a datetime", total_time_online=0)

        with patch("user_auth.auth.db.session") as mock_session:
            try:
                update_user_activity(mock_user)
            except Exception as e:
                assert isinstance(e, TypeError)
