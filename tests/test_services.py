from unittest.mock import AsyncMock
import pytest
from core.exceptions import (
    DuplicateResourceError,
    ForbiddenError,
    InvalidCredentialsError,
    ResourceNotFoundError,
)
from modules.users.models import User
from modules.users.schemas import UserCreate, UserUpdate
from modules.users.service import UserService


@pytest.mark.anyio
async def test_user_service_duplicate_username():
    mock_repo = AsyncMock()
    mock_repo.get_by_username.return_value = User(id=1, username="existing", email="test@test.com", password_hash="hash")
    service = UserService(mock_repo)

    with pytest.raises(DuplicateResourceError, match="Username already exists"):
        await service.register_user(UserCreate(username="existing", email="new@test.com", password="password123"))


@pytest.mark.anyio
async def test_user_service_duplicate_email():
    mock_repo = AsyncMock()
    mock_repo.get_by_username.return_value = None
    mock_repo.get_by_email.return_value = User(id=1, username="other", email="existing@test.com", password_hash="hash")
    service = UserService(mock_repo)

    with pytest.raises(DuplicateResourceError, match="Email already exists"):
        await service.register_user(UserCreate(username="newuser", email="existing@test.com", password="password123"))


@pytest.mark.anyio
async def test_user_service_authenticate_user_not_found():
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = None
    service = UserService(mock_repo)

    with pytest.raises(InvalidCredentialsError, match="Incorrect email or password"):
        await service.authenticate("notfound@test.com", "password123")


@pytest.mark.anyio
async def test_user_service_update_unauthorized():
    mock_repo = AsyncMock()
    service = UserService(mock_repo)

    with pytest.raises(ForbiddenError, match="Not authorized to update this user"):
        await service.update_user(user_id=2, current_user_id=1, data=UserUpdate(username="newname"))


@pytest.mark.anyio
async def test_user_service_get_by_id_not_found():
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = None
    service = UserService(mock_repo)

    with pytest.raises(ResourceNotFoundError, match="User not found"):
        await service.get_by_id(999)
