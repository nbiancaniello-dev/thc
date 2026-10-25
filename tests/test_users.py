import pytest
from httpx import AsyncClient

from tests.helpers import create_test_user, login_user, auth_header


@pytest.mark.anyio
async def test_create_user_validation_error(client: AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "username": "testuser",
        },
    )

    assert response.status_code == 422
    assert "email" in response.text
    assert "password" in response.text


@pytest.mark.anyio
async def test_create_user_duplicate_email(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/api/users",
        json={
            "username": "different_user",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


@pytest.mark.anyio
async def test_create_user_duplicate_username(client: AsyncClient):
    await create_test_user(client, username="testuser", email="test1@example.com")

    response = await client.post(
        "/api/users",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


@pytest.mark.anyio
async def test_create_user_success(client: AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.anyio
async def test_login_success(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/api/users/token",
        data={
            "username": "test@example.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_invalid_password(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/api/users/token",
        data={
            "username": "test@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.anyio
async def test_login_user_not_found(client: AsyncClient):
    response = await client.post(
        "/api/users/token",
        data={
            "username": "nonexistent@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.anyio
async def test_get_current_user_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.get(
        "/api/users/me",
        headers=auth_header(token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


@pytest.mark.anyio
async def test_get_current_user_invalid_token(client: AsyncClient):
    response = await client.get(
        "/api/users/me",
        headers=auth_header("invalid_token"),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


@pytest.mark.anyio
async def test_get_all_users_success(client: AsyncClient):
    user1 = await create_test_user(client, username="user1", email="user1@example.com")
    user2 = await create_test_user(client, username="user2", email="user2@example.com")

    response = await client.get("/api/users")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    usernames = [u["username"] for u in data]
    assert "user1" in usernames
    assert "user2" in usernames


@pytest.mark.anyio
async def test_get_all_users_empty(client: AsyncClient):
    response = await client.get("/api/users")

    assert response.status_code == 404
    assert response.json()["detail"] == "No users found"


@pytest.mark.anyio
async def test_get_user_by_id_success(client: AsyncClient):
    user = await create_test_user(client)
    user_id = user["id"]

    response = await client.get(f"/api/users/{user_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "testuser"


@pytest.mark.anyio
async def test_get_user_by_id_not_found(client: AsyncClient):
    response = await client.get("/api/users/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.anyio
async def test_update_user_success(client: AsyncClient):
    user = await create_test_user(client)
    user_id = user["id"]
    token = await login_user(client)

    response = await client.patch(
        f"/api/users/{user_id}",
        json={"username": "updateduser"},
        headers=auth_header(token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updateduser"
    assert data["email"] == "test@example.com"


@pytest.mark.anyio
async def test_update_user_unauthorized(client: AsyncClient):
    user1 = await create_test_user(client, username="user1", email="user1@example.com")
    user2 = await create_test_user(client, username="user2", email="user2@example.com")
    token = await login_user(client, email="user2@example.com")

    response = await client.patch(
        f"/api/users/{user1['id']}",
        json={"username": "hacker"},
        headers=auth_header(token),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to update this user"


@pytest.mark.anyio
async def test_update_user_not_found(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.patch(
        "/api/users/9999",
        json={"username": "newname"},
        headers=auth_header(token),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to update this user"


@pytest.mark.anyio
async def test_update_user_duplicate_username(client: AsyncClient):
    user1 = await create_test_user(client, username="user1", email="user1@example.com")
    user2 = await create_test_user(client, username="user2", email="user2@example.com")
    token = await login_user(client, email="user2@example.com")

    response = await client.patch(
        f"/api/users/{user2['id']}",
        json={"username": "user1"},
        headers=auth_header(token),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


@pytest.mark.anyio
async def test_update_user_duplicate_email(client: AsyncClient):
    user1 = await create_test_user(client, username="user1", email="user1@example.com")
    user2 = await create_test_user(client, username="user2", email="user2@example.com")
    token = await login_user(client, email="user2@example.com")

    response = await client.patch(
        f"/api/users/{user2['id']}",
        json={"email": "user1@example.com"},
        headers=auth_header(token),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


@pytest.mark.anyio
async def test_update_user_partial_fields(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    response = await client.patch(
        f"/api/users/{user['id']}",
        json={"username": "newtestuser"},
        headers=auth_header(token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newtestuser"
    assert data["email"] == "test@example.com"


@pytest.mark.anyio
async def test_delete_user_success(client: AsyncClient):
    user = await create_test_user(client)
    user_id = user["id"]
    token = await login_user(client)

    response = await client.delete(
        f"/api/users/{user_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 204

    get_response = await client.get(f"/api/users/{user_id}")
    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_delete_user_unauthorized(client: AsyncClient):
    user1 = await create_test_user(client, username="user1", email="user1@example.com")
    user2 = await create_test_user(client, username="user2", email="user2@example.com")
    token = await login_user(client, email="user2@example.com")

    response = await client.delete(
        f"/api/users/{user1['id']}",
        headers=auth_header(token),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to delete this user"


@pytest.mark.anyio
async def test_delete_user_not_found(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.delete(
        "/api/users/9999",
        headers=auth_header(token),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to delete this user"
