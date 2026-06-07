"""Data Source aggregate root.

Represents an external data provider (e.g. Yahoo Finance) in the
bi-temporal model.  Mutations produce new immutable versions.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class DataSourceAggregate:
    """Aggregate root for the Data Source bounded context.

    Attributes
    ----------
    id : str
        Unique provider key (e.g. ``YFINANCE``).
    system_date : datetime
        Timestamp of this version (UTC).
    name : str
        Human-readable provider name.
    description : str
        Free-text description.
    attributes : set[str]
        Set of data-point names supported by the provider.
    """

    id: str
    system_date: datetime
    name: str = ""
    description: str = ""
    attributes: set[str] = field(default_factory=set)

    @property
    def is_deleted(self) -> bool:
        """Return ``True`` if this version has been soft-deleted."""
        return "deleted" in self.attributes

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        attributes: set[str] | None = None,
    ) -> "DataSourceAggregate":
        """Return a new version with updated fields.

        Only non-``None`` arguments overwrite existing values.
        """
        return DataSourceAggregate(
            id=self.id,
            system_date=datetime.now(UTC),
            name=name if name is not None else self.name,
            description=description if description is not None else self.description,
            attributes=attributes if attributes is not None else self.attributes,
        )
