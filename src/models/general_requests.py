from dataclasses import Field
from typing import List
from pydantic import BaseModel


class IssueUpdateRequest(BaseModel):
    summary: str
    description: str
    usesMarkdown: bool
    markdownEmbeddings: List
    fields: List[Field]

    class Config:
        extra = "forbid"
