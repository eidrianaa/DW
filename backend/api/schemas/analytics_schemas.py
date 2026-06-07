from pydantic import BaseModel

class TotalRow(BaseModel):
    asset_id: str
    business_date_year: int
    count: int

class TotalsResponse(BaseModel):
    totals: list[TotalRow]

class PredictionRow(BaseModel):
    seconds: int
    actual_open: float
    predicted_open: float

class PredictionsResponse(BaseModel):
    predictions: list[PredictionRow]
