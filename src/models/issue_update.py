from pydantic import BaseModel
from models.issue_update_request import IssueUpdateRequest


class IssueUpdate(BaseModel):
    id: str = ""
    time: str = ""
    description: str = ""
    type: str = ""
    state: str = ""

    def __iter__(self):
        return iter((self.id, self.time, self.description, self.type, self.state))

    def to_request(self) -> IssueUpdateRequest:
        return IssueUpdateRequest(
            duration=int(self.time) if self.time.isdigit() else None,
            author="author_id",
            text=self.description,
            type=self.type or None
        )
