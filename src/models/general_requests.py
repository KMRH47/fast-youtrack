from pydantic import BaseModel
from typing import Optional, List

from models.work_item_base import WorkItem

class FieldStyle(WorkItem):
    background: Optional[str]
    foreground: Optional[str]

class Value(WorkItem):
    color: Optional[FieldStyle]

class Field(WorkItem):
    value: Optional[Value]

class IssueUpdateRequest(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    usesMarkdown: Optional[bool] = None
    markdownEmbeddings: List = []
    fields: Optional[List[Field]] = None

    class Config:
        arbitrary_types_allowed = True
