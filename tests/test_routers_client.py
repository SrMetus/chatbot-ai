import pytest


class TestReadClients:
    def test_list_clients_public(self, client):
        response = client.get("/api/v1/clients/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_clients_with_data(self, client, sample_client):
        response = client.get("/api/v1/clients/")
        data = response.json()
        assert len(data) >= 1
        assert data[0]["email"] == sample_client.email

    def test_get_client_by_id(self, client, sample_client):
        response = client.get(f"/api/v1/clients/{sample_client.id}")
        assert response.status_code == 200
        assert response.json()["name"] == sample_client.name

    def test_get_client_not_found(self, client):
        response = client.get("/api/v1/clients/99999")
        assert response.status_code == 404


class TestCreateClient:
    def test_create_client_requires_auth(self, client):
        response = client.post(
            "/api/v1/clients/",
            json={
                "name": "Nueva Notaría",
                "email": "nueva@notaria.cl",
                "business_type": "notaría",
            },
        )
        assert response.status_code == 401

    def test_create_client_success(self, client, auth_headers):
        response = client.post(
            "/api/v1/clients/",
            json={
                "name": "Nueva Notaría",
                "email": "nueva@notaria.cl",
                "business_type": "notaría chilena",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Nueva Notaría"
        assert data["is_active"] is True

    def test_create_client_duplicate_email(self, client, auth_headers, sample_client):
        response = client.post(
            "/api/v1/clients/",
            json={
                "name": "Otra Notaría",
                "email": sample_client.email,
                "business_type": "notaría",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()


class TestUpdateClient:
    def test_update_requires_auth(self, client, sample_client):
        response = client.patch(
            f"/api/v1/clients/{sample_client.id}",
            json={"name": "Nuevo Nombre"},
        )
        assert response.status_code == 401

    def test_update_success(self, client, auth_headers, sample_client):
        response = client.patch(
            f"/api/v1/clients/{sample_client.id}",
            json={"name": "Notaría Actualizada"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Notaría Actualizada"

    def test_update_not_found(self, client, auth_headers):
        response = client.patch(
            "/api/v1/clients/99999",
            json={"name": "No existe"},
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestDeleteClient:
    def test_delete_requires_auth(self, client, sample_client):
        response = client.delete(f"/api/v1/clients/{sample_client.id}")
        assert response.status_code == 401

    def test_delete_soft_deletes(self, client, auth_headers, sample_client):
        response = client.delete(
            f"/api/v1/clients/{sample_client.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_delete_not_found(self, client, auth_headers):
        response = client.delete(
            "/api/v1/clients/99999",
            headers=auth_headers,
        )
        assert response.status_code == 404
