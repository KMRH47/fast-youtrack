from typing import Literal, Optional
from pydantic import BaseModel, Field


class WorkItem(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    type_: Optional[str] = Field(None, alias='$type')


YoutrackResponseField = Literal["State", "Priority",
                                "Type", "Assignee",
                                "Fix versions", "Affected versions"]
