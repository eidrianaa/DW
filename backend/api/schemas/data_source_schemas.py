from pydantic import BaseModel

class RegisterDataSourceRequest(BaseModel):
    data_source_id: str
    name: str
    description: str = ""
    attributes: list[str] | None = None
