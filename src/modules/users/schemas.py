from pydantic import BaseModel, ConfigDict, Field, EmailStr

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr = Field(max_length=50)
    dragon_ball_ids: list[int] | None = Field(default=None)

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=20)
    email: EmailStr | None = Field(default=None, max_length=50)
    dragon_ball_ids: list[int] | None = Field(default=None)

class Token(BaseModel):
    access_token: str
    token_type: str

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    dragon_ball_ids: list[int] | None = Field(default=None)

class UserPrivate(UserPublic):
    email: EmailStr

class DragonBallCharacter(BaseModel):
    id: int
    name: str

class UserDragonBalls(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    dragon_ball_ids: list[int] | None = Field(default=None)
    dragon_balls: list[DragonBallCharacter] = Field(default_factory=list)

class UserDragonBallIdsUpdate(BaseModel):
    dragon_ball_ids: list[int]
