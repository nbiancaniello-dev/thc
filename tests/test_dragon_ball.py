import httpx
import pytest
from httpx import AsyncClient

from clients.dragon_ball_client import DragonBallClient

# All tests here run against the fake API from the autouse
# `mock_dragon_ball_api` fixture in conftest.py (data in tests/helpers.py).


async def create_user(client: AsyncClient, username: str, dragon_ball_ids=None) -> dict:
    response = await client.post(
        "/api/users",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "testpassword123",
            "dragon_ball_ids": dragon_ball_ids,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.anyio
async def test_get_user_by_id_includes_character_names(client, mock_dragon_ball_api):
    user = await create_user(client, "goku_fan", [1, 2])

    response = await client.get(f"/api/users/{user['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "goku_fan"
    assert data["dragon_ball_ids"] == [1, 2]
    assert data["dragon_balls"] == [
        {"id": 1, "name": "Goku"},
        {"id": 2, "name": "Vegeta"},
    ]
    assert sorted(mock_dragon_ball_api) == ["/api/characters/1", "/api/characters/2"]


@pytest.mark.anyio
async def test_get_users_includes_character_names(client, mock_dragon_ball_api):
    await create_user(client, "user_a", [1, 2])
    await create_user(client, "user_b", [2, 3])
    await create_user(client, "user_c")

    response = await client.get("/api/users")

    assert response.status_code == 200
    by_username = {u["username"]: u for u in response.json()}
    assert [c["name"] for c in by_username["user_a"]["dragon_balls"]] == ["Goku", "Vegeta"]
    assert [c["name"] for c in by_username["user_b"]["dragon_balls"]] == ["Vegeta", "Piccolo"]
    assert by_username["user_c"]["dragon_balls"] == []
    # Id 2 is shared by two users but requested only once
    assert sorted(mock_dragon_ball_api) == [
        "/api/characters/1",
        "/api/characters/2",
        "/api/characters/3",
    ]


@pytest.mark.anyio
async def test_user_without_ids_makes_no_api_calls(client, mock_dragon_ball_api):
    user = await create_user(client, "no_ids")

    response = await client.get(f"/api/users/{user['id']}")

    assert response.status_code == 200
    assert response.json()["dragon_balls"] == []
    assert mock_dragon_ball_api == []


@pytest.mark.anyio
async def test_unknown_character_ids_are_skipped(client):
    user = await create_user(client, "lost_ids", [1, 999])

    response = await client.get(f"/api/users/{user['id']}")

    assert response.status_code == 200
    assert response.json()["dragon_balls"] == [{"id": 1, "name": "Goku"}]


@pytest.mark.anyio
async def test_client_keeps_only_id_and_name(mock_dragon_ball_api):
    result = await DragonBallClient().get_dragon_ball_characters_by_ids([1, 1, 42])

    assert result == [{"id": 1, "name": "Goku"}]
    assert sorted(mock_dragon_ball_api) == ["/api/characters/1", "/api/characters/42"]
    assert await DragonBallClient().get_dragon_ball_characters_by_ids(None) == []


@pytest.mark.anyio
async def test_client_returns_empty_list_when_api_is_down():
    def unreachable(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("API unreachable", request=request)

    client = DragonBallClient(transport=httpx.MockTransport(unreachable))

    assert await client.get_dragon_ball_characters_by_ids([1, 2]) == []
