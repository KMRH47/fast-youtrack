from datetime import datetime
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


class Type(WorkItem):
    id: Optional[str] = None
    name: Optional[str] = None
    localizedName: Optional[str] = None
    isDefault: Optional[bool] = None
    isAutoAttached: Optional[bool] = None
    presentation: Optional[str] = None


class Duration(WorkItem):
    minutes: int
    presentation: Optional[str] = None


class AddSpentTimeRequest(WorkItem):
    duration: Duration
    date: int = Field(alias="date_millis")
    text: Optional[str] = Field(None, alias="description")
    type: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
