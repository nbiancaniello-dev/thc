from httpx import AsyncClient


async def create_test_user(
    client: AsyncClient,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpassword123",
) -> dict:
    response = await client.post(
        "/api/users",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    return response.json()


async def login_user(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "testpassword123",
) -> str:
    response = await client.post(
        "/api/users/token",
        data={
            "username": email,
            "password": password,
        },
    )
    assert response.status_code == 200, f"Failed to login: {response.text}"
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# Fake payloads shaped like GET https://dragonball-api.com/api/characters/{id}
FAKE_DRAGON_BALL_CHARACTERS: dict[int, dict] = {
    1: {
        "id": 1,
        "name": "Goku",
        "ki": "60.000.000",
        "maxKi": "90 Septillion",
        "race": "Saiyan",
        "gender": "Male",
        "affiliation": "Z Fighter",
        "originPlanet": {"id": 2, "name": "Tierra"},
        "transformations": [],
    },
    2: {
        "id": 2,
        "name": "Vegeta",
        "ki": "54.000.000",
        "maxKi": "19.84 Septillion",
        "race": "Saiyan",
        "gender": "Male",
        "affiliation": "Z Fighter",
        "originPlanet": {"id": 3, "name": "Vegeta"},
        "transformations": [],
    },
    3: {
        "id": 3,
        "name": "Piccolo",
        "ki": "2.000.000",
        "maxKi": "500.000.000",
        "race": "Namekian",
        "gender": "Male",
        "affiliation": "Z Fighter",
        "originPlanet": {"id": 1, "name": "Namek"},
        "transformations": [],
    },
}
