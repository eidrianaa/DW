"""Asset aggregate root.

Represents a financial asset (e.g. a stock ticker) in the bi-temporal
model.  Every mutation produces a new instance with a fresh
``system_date``, preserving the full version history.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class AssetAggregate:
    """Aggregate root for the Asset bounded context.

    Attributes
    ----------
    id : str
        Unique identifier, typically ``<provider>/<ticker>``.
    system_date : datetime
        Timestamp of this version (UTC).
    name : str
        Human-readable asset name.
    description : str
        Free-text description.
    attributes : dict[str, str]
        Arbitrary key-value metadata.
    """

    id: str
    system_date: datetime
    name: str = ""
    description: str = ""
    attributes: dict[str, str] = field(default_factory=dict)

    @property
    def is_deleted(self) -> bool:
        """Return ``True`` if this version has been soft-deleted."""
        return self.attributes.get("deleted") == "true"

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        attributes: dict[str, str] | None = None,
    ) -> "AssetAggregate":
        """Return a new version of the aggregate with updated fields.

        Only non-``None`` arguments overwrite existing values.
        """
        return AssetAggregate(
            id=self.id,
            system_date=datetime.now(UTC),
            name=name if name is not None else self.name,
            description=description if description is not None else self.description,
            attributes=attributes if attributes is not None else self.attributes,
        )

    def mark_deleted(self) -> "AssetAggregate":
        """Return a new version flagged as deleted."""
        return AssetAggregate(
            id=self.id,
            system_date=datetime.now(UTC),
            name=self.name,
            description=self.description,
            attributes={**self.attributes, "deleted": "true"},
        )
