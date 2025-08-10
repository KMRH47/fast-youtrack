import sys
import os
from pathlib import Path

from pydantic import BaseModel

from errors.user_error import UserError


class AppArgs(BaseModel):
    passphrase: str
    subdomain: str
    max_log_size_bytes: int = 5 * 1024 * 1024  # Default 5MB

    @property
    def base_url(self) -> str:
        return f"https://{self.subdomain}.youtrack.cloud/api"

    @property
    def base_dir(self) -> str:
        if getattr(sys, 'frozen', False):
            exe_path = Path(sys.executable).resolve()
            if sys.platform == "darwin":
                try:
                    project_root = exe_path.parents[3]
                except IndexError:
                    project_root = exe_path.parent
            else:
                project_root = exe_path.parent
        else:
            project_root = Path(__file__).parent.parent.absolute()

        return str(project_root / "user" / self.subdomain)

    @classmethod
    def from_sys_args(cls) -> "AppArgs":
        if len(sys.argv) < 3:
            raise UserError("Passphrase and subdomain are required.\n\n")

        passphrase = sys.argv[1]
        subdomain = sys.argv[2]

        if not passphrase or not subdomain:
            raise UserError("Passphrase and subdomain are required and cannot be empty.\n\n")

        args = {
            "passphrase": passphrase,
            "subdomain": subdomain
        }

        for i in range(3, len(sys.argv)):
            if sys.argv[i] == "--max-log-size" and i + 1 < len(sys.argv):
                try:
                    size_mb = float(sys.argv[i + 1])
                    args["max_log_size_bytes"] = int(size_mb * 1024 * 1024)
                except ValueError:
                    raise UserError(
                        f"Invalid log size: {sys.argv[i+1]}. Must be a number in MB.")

        return cls(**args)
