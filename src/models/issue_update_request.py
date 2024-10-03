from pydantic import BaseModel


class IssueUpdateRequest(BaseModel):
    id: str = ""
    time: str = ""
    description: str = ""
    type: str = ""
    state: str = ""

    def __iter__(self):
        return iter((self.id, self.time, self.description, self.type, self.state))
