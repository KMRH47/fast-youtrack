from pydantic import BaseModel
from typing import Optional

from models.work_item_base import WorkItem


class Duration(BaseModel):
    minutes: int


class Author(WorkItem):
    pass


class IssueType(WorkItem):
    pass


class IssueState(WorkItem):
    pass


class IssueUpdateRequest(BaseModel):
    author: Author
    duration: Duration
    text: Optional[str] = None
    type: Optional[IssueType] = None
