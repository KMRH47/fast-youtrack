from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    login: str
    email: str
    name: str
