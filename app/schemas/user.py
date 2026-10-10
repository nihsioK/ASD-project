from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserCredentials(BaseModel):
    email: str = Field(min_length=3, max_length=255, pattern=r"^[^@\s]+@[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, email: object) -> object:
        # runs before the pattern check, so " A@B.kz " is accepted as "a@b.kz"
        return email.strip().lower() if isinstance(email, str) else email


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
