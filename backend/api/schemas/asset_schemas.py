from pydantic import BaseModel

class CreateAssetRequest(BaseModel):
    asset_id: str
    name: str
    description: str = ""
    attributes: dict[str, str] | None = None

class UpdateAssetRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    attributes: dict[str, str] | None = None
