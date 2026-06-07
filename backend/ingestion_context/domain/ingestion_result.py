from dataclasses import dataclass

@dataclass(frozen=True)
class IngestionResult:
    fetched: int
    stored: int
    skipped: int
    errors: int

    @property
    def success_rate(self) -> float:
        if self.fetched == 0:
            return 0.0
        return (self.stored / self.fetched) * 100
