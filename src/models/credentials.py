from pydantic import BaseModel, Field


class Credentials(BaseModel):
    subdomain: str = Field(...,
                           description="Subdomain of the YouTrack instance")
    bearer_token: str = Field(...,
                              description="Bearer token for authentication")
