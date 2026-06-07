from pydantic import BaseModel
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel):
    items: list
    offset: int
    limit: int
    total: int
    has_next: bool
