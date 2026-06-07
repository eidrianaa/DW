from dataclasses import dataclass
from shared.events.domain_event import DomainEvent

@dataclass(frozen=True)
class AssetCreated(DomainEvent):
    asset_id: str = ""

@dataclass(frozen=True)
class AssetUpdated(DomainEvent):
    asset_id: str = ""

@dataclass(frozen=True)
class AssetDeleted(DomainEvent):
    asset_id: str = ""
