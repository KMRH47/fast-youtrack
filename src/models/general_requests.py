from dataclasses import Field
from typing import List, Optional
from pydantic import BaseModel


class IssueUpdateRequest(BaseModel):
    summary: Optional[str]
    description: Optional[str]
    usesMarkdown: Optional[bool]
    markdownEmbeddings: List = []
    fields: Optional[List[Field]] = None

    class Config:
        arbitrary_types_allowed = True
