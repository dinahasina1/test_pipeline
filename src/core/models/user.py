from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(alias="userId")
    name: str
    email: EmailStr