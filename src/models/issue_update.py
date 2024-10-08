from pydantic import BaseModel


class IssueUpdate(BaseModel):
    id: str = ""
    time: str = ""
    description: str = ""
    state: str = ""
    type: str = ""

    def __iter__(self):
        return iter((self.id, self.time, self.description, self.type, self.state))
