from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    get_current_user,
)
from unittest.mock import patch
from fastapi import HTTPException
import pytest


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        hashed = hash_password("mypassword")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        hashed = hash_password("correct-password")
        assert verify_password("correct-password", hashed) is True

    def test_verify_password_wrong(self):
        hashed = hash_password("correct-password")
        assert verify_password("wrong-password", hashed) is False

    def test_hash_is_different_each_time(self):
        pwd = "samepassword"
        h1 = hash_password(pwd)
        h2 = hash_password(pwd)
        assert h1 != h2


class TestJWTTokens:
    def test_create_access_token_returns_string(self):
        token = create_access_token(data={"sub": "user@test.cl"})
        assert isinstance(token, str)
        assert len(token.split(".")) == 3

    def test_decode_valid_token(self):
        token = create_access_token(data={"sub": "user@test.cl"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user@test.cl"

    def test_decode_invalid_token_returns_none(self):
        payload = decode_access_token("invalid.token.here")
        assert payload is None

    def test_decode_expired_token_returns_none(self):
        from jose import jwt
        from datetime import datetime, timedelta, timezone
        expired = jwt.encode(
            {"sub": "user@test.cl", "exp": datetime(2020, 1, 1, tzinfo=timezone.utc)},
            "test-secret",
            algorithm="HS256",
        )
        from app.core.security import decode_access_token
        with __import__('unittest').mock.patch('app.core.security.settings.SECRET_KEY', 'test-secret'):
            with __import__('unittest').mock.patch('app.core.security.settings.ALGORITHM', 'HS256'):
                payload = decode_access_token(expired)
        assert payload is None


class TestGetCurrentUser:
    def test_returns_user_for_valid_token(self, db_session, sample_user):
        token = create_access_token(data={"sub": sample_user.email})
        user = get_current_user(token=token, db=db_session)
        assert user is not None
        assert user.email == sample_user.email

    def test_raises_401_for_invalid_token(self, db_session):
        with pytest.raises(HTTPException) as exc:
            get_current_user(token="invalid-token", db=db_session)
        assert exc.value.status_code == 401

    def test_raises_401_for_nonexistent_user(self, db_session):
        token = create_access_token(data={"sub": "noexists@test.cl"})
        with pytest.raises(HTTPException) as exc:
            get_current_user(token=token, db=db_session)
        assert exc.value.status_code == 401

    def test_raises_401_for_token_without_sub(self, db_session):
        token = create_access_token(data={"other": "value"})
        with pytest.raises(HTTPException) as exc:
            get_current_user(token=token, db=db_session)
        assert exc.value.status_code == 401
