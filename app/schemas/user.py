from pydantic import BaseModel, ConfigDict, Field


class UserCredentials(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
