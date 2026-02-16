from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    """
    Represents a user entity from the source CSV.
    Uses aliases to map CSV headers to standard Python naming.
    """
    id: int = Field(alias="userId")
    name: str
    email: EmailStr

    class Config:
        populate_by_name = True