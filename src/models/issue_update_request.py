from typing import List
from pydantic import BaseModel


class IssueState(BaseModel):
    current: str = ""
    available_states: List[str] = []


class IssueUpdateRequest(BaseModel):
    id: str = ""
    time: str = ""
    description: str = ""
    type: str = ""
    state: IssueState = IssueState(current="", available_states=[])

    def __iter__(self):
        return iter((self.id, self.time, self.description, self.type, self.state))
