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


class Duration(WorkItem):
    minutes: int
    presentation: Optional[str] = None


class Type(WorkItem):
    id: Optional[str] = None
    name: Optional[str] = None
    localizedName: Optional[str] = None
    isDefault: Optional[bool] = None
    isAutoAttached: Optional[bool] = None
    presentation: Optional[str] = None


class AddSpentTimeRequest(WorkItem):
    duration: Duration
    text: Optional[str] = None
    type: Optional[str] = None
    date_millis: Optional[int] = Field(default=None, alias="date")

    class Config:
        arbitrary_types_allowed = True
