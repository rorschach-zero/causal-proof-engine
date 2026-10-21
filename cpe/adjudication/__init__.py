"""Four timestamps, resolution rules and adjudication (``17`` section 3 item 1; hand-off section 3.1).

- ``knowable_at`` is the earliest time at which the outcome was publicly determinable: the evidenced publication
  time, the occurrence time when the occurrence is itself a public act, or logical finality (deadline + latency
  window), whichever is earliest (RC-52, RC-77, RC-146).
- The latency window is applied to the evidenced publication time of the source record, never to registry
  receipt; a receipt lag is an integrity incident, not an outcome (RC-105).
- The disposition at logical finality is immutable: NO (or, for a terminal falsifier, YES) when an archived
  observation shows no record at or after finality, an adjudicated VOID when the source rule's failure condition
  holds, otherwise OPEN until the observer has read the source; a later report of timely occurrence is a
  source-latency defect and changes nothing (RC-88, RC-113).
- A resolution record names the archived source content it rests on (content-addressed by SHA-256, supplied by
  the caller, never fetched); its claim is derived from that content by the registered predicate (PR #18
  4329664953; hand-off section 3.1).
- Breaches are classes of a member's ``knowable_at`` against the registration time, the arm cutoffs and the
  issuance close (RC-135, RC-139, RC-163); what they do in a statistic is item 3 and is not built here.
"""
from cpe.adjudication.breaches import BreachReport, classify_breaches
from cpe.adjudication.content import ArchivedContent
from cpe.adjudication.eligibility import ForecastStatus, classify_forecast, cluster_knowable_time
from cpe.adjudication.records import AbsenceObservation, ResolutionRecord, SourceRule, SourceStatus
from cpe.adjudication.predicate import MEDIA_TYPE_JSON, evaluate
from cpe.adjudication.registry import AdjudicationRegistry
from cpe.adjudication.rules import Adjudication, Disposition, adjudicate

__all__ = [
    "AbsenceObservation",
    "Adjudication",
    "AdjudicationRegistry",
    "ArchivedContent",
    "BreachReport",
    "Disposition",
    "MEDIA_TYPE_JSON",
    "ForecastStatus",
    "ResolutionRecord",
    "SourceRule",
    "SourceStatus",
    "adjudicate",
    "classify_breaches",
    "classify_forecast",
    "cluster_knowable_time",
    "evaluate",
]
