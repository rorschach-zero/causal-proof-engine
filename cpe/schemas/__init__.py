"""Typed schemas of ``17`` section 3 item 1.

Every schema is an immutable dataclass with ``from_payload`` (strict: unknown keys are refused, so a record cannot
carry a field the schema does not define) and ``to_payload`` (the JSON form the ledger stores). Validation is
structural; the registry rules that relate records to each other live in the registries.
"""
from cpe.schemas.capability import Capability
from cpe.schemas.event import ClusterRecord, EventSpec, ResolutionPredicate, ResolutionTimestamps
from cpe.schemas.forecast import ArmVersion, Forecast, JevRecord, effective_cutoff
from cpe.schemas.research_output import ResearchOutput

__all__ = [
    "ArmVersion",
    "Capability",
    "ClusterRecord",
    "EventSpec",
    "Forecast",
    "JevRecord",
    "ResearchOutput",
    "ResolutionPredicate",
    "ResolutionTimestamps",
    "effective_cutoff",
]
