from datetime import date
from pydantic import BaseModel, Field
from typing import Optional, List

from models.work_item_base import WorkItem


class FieldStyle(WorkItem):
    background: Optional[str]
    foreground: Optional[str]


class Value(WorkItem):
    color: Optional[FieldStyle]


class WorkItemField(WorkItem):
    value: Optional[Value]


class IssueUpdateRequest(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    usesMarkdown: Optional[bool] = None
    markdownEmbeddings: List = []
    fields: Optional[List[WorkItemField]] = None

    class Config:
        arbitrary_types_allowed = True


class AddSpentTimeRequest(WorkItem):
    duration: Optional[int] = None
    description: Optional[str] = None
    type: Optional[str] = None
    date_: Optional[date] = Field(alias='date')

    class Config:
        arbitrary_types_allowed = True

