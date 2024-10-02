from typing import List
from pydantic import BaseModel


class StoryState(BaseModel):
    current: str = ""
    available_states: List[str] = []


class StoryUpdate(BaseModel):
    issue_id: str = ""
    time: str = ""
    description: str = ""
    type: str = ""
    state: StoryState = StoryState(current="", available_states=[])

    def __iter__(self):
        return iter((self.issue_id, self.time, self.description, self.type, self.state))
