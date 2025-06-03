from typing import Optional

from pydantic import BaseModel


class EnvVar(BaseModel):
    name: str
    description: str
    required: bool = True
    default: Optional[str] = None
