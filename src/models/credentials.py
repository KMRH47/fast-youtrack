from typing import Optional
from pydantic import BaseModel, Field


class Credentials(BaseModel):
    subdomain: str = Field(...,
                           description="Subdomain of the YouTrack instance")
    bearer_token: str = Field(...,
                              description="Bearer token for authentication")
    author_id: str = Field(..., description="ID of the author")
    author_name: str = Field(..., description="Name of the author")
