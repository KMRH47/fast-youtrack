import sys
from pathlib import Path

from pydantic import BaseModel

from errors.user_error import UserError


class AppArgs(BaseModel):
    passphrase: str
    subdomain: str

    @property
    def base_url(self) -> str:
        return f"https://{self.subdomain}.youtrack.cloud/api"

    @property
    def base_dir(self) -> str:
        return str(Path(__file__).parent.parent / "user" / self.subdomain)

    @classmethod
    def from_sys_args(cls) -> "AppArgs":
        if len(sys.argv) < 3:
            raise UserError("Passphrase and subdomain are required.\n\n")
        return cls(passphrase=sys.argv[1], subdomain=sys.argv[2])
