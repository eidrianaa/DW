from pydantic import BaseModel

class TimeSeriesRecord(BaseModel):
    businessDate: str
    values: dict[str, float | int | str]

class TimeSeriesData(BaseModel):
    assetId: str
    datasourceId: str
    records: list[TimeSeriesRecord]

class TimeSeriesResponse(BaseModel):
    data: TimeSeriesData
    attributes: list[str] | None = None
