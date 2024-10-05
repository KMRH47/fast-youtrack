from pydantic import BaseModel
from typing import Optional

class Duration(BaseModel):
    minutes: int

class Author(BaseModel):
    id: str

class IssueType(BaseModel):
    id: str

class IssueUpdateRequest(BaseModel):
    duration: Duration
    author: Author
    text: str
    type: Optional[IssueType] = None