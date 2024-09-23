from pydantic import BaseModel


class WorkItemResponse(BaseModel):
    id: str
    name: str
