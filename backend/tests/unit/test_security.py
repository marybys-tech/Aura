"""Unit tests for JWT token creation, decoding, and hashing."""

import hashlib
import uuid

import jwt
import pytest

from app.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_token,
)


class TestCreateAndDecodeAccessToken:
    def test_roundtrip(self):
        uid = uuid.uuid4()
        token = create_access_token(uid)
        payload = decode_access_token(token)
        assert payload["sub"] == str(uid)

    def test_contains_exp_and_iat(self):
        token = create_access_token(uuid.uuid4())
        payload = decode_access_token(token)
        assert "exp" in payload
        assert "iat" in payload
        assert payload["exp"] > payload["iat"]

    def test_invalid_token_raises(self):
        with pytest.raises(jwt.exceptions.DecodeError):
            decode_access_token("not-a-real-token")

    def test_tampered_token_raises(self):
        token = create_access_token(uuid.uuid4())
        tampered = token[:-4] + "XXXX"
        with pytest.raises(jwt.exceptions.InvalidSignatureError):
            decode_access_token(tampered)

    def test_wrong_secret_raises(self):
        uid = uuid.uuid4()
        token = create_access_token(uid)
        with pytest.raises(jwt.exceptions.InvalidSignatureError):
            jwt.decode(token, "wrong-secret", algorithms=[settings.JWT_ALGORITHM])

    def test_different_users_get_different_tokens(self):
        t1 = create_access_token(uuid.uuid4())
        t2 = create_access_token(uuid.uuid4())
        assert t1 != t2


class TestGenerateRefreshToken:
    def test_returns_string(self):
        token = generate_refresh_token()
        assert isinstance(token, str)

    def test_is_url_safe(self):
        token = generate_refresh_token()
        safe_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")
        assert all(c in safe_chars for c in token)

    def test_tokens_are_unique(self):
        tokens = {generate_refresh_token() for _ in range(50)}
        assert len(tokens) == 50

    def test_sufficient_length(self):
        token = generate_refresh_token()
        assert len(token) >= 32


class TestHashToken:
    def test_deterministic(self):
        assert hash_token("abc") == hash_token("abc")

    def test_is_sha256_hex(self):
        h = hash_token("test")
        assert len(h) == 64
        assert h == hashlib.sha256(b"test").hexdigest()

    def test_different_inputs_different_hashes(self):
        assert hash_token("a") != hash_token("b")
