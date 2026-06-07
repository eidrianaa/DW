from pydantic import BaseModel

class IngestionStatsResponse(BaseModel):
    fetched: int
    stored: int
    skipped: int
    errors: int
