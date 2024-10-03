from typing import Optional
from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    login: Optional[str] = ""
    email: Optional[str] = ""
    name: str
