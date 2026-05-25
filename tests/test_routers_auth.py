import pytest


class TestRegister:
    def test_register_success(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "nuevo@notaria.cl", "password": "secret123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "nuevo@notaria.cl"
        assert "id" in data

    def test_register_duplicate_email(self, client, sample_user):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": sample_user.email, "password": "secret123"},
        )
        assert response.status_code == 400
        assert "ya registrado" in response.json()["detail"].lower()

    def test_register_password_not_in_response(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "seguro@notaria.cl", "password": "mipassword"},
        )
        assert response.status_code == 200
        assert "password" not in response.json()


class TestLogin:
    def test_login_success(self, client, sample_user):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": sample_user.email, "password": "testpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, sample_user):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": sample_user.email, "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "noexiste@test.cl", "password": "pass123"},
        )
        assert response.status_code == 401
