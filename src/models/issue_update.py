from pydantic import BaseModel


class IssueUpdate(BaseModel):
    id: str = ""
    time: str = ""
    description: str = ""
    state: str = ""
    type: str = ""
