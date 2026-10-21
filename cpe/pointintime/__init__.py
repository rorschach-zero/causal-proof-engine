"""Point-in-time feature store with as-of reads, and the leak detector of T-15 (``17`` section 3 item 1, RC-79,
RC-86; hand-off section 3.1, built after the OD9a wording was merged into ``AGENTS.md``, PR #30).

- Rows are (entity, feature, value, ``observed_at``, ``available_at``, vintage id), written once on the ledger.
- The as-of reader is bound to a forecast's evidence cutoff and never returns a row available after it; at a cutoff
  it returns, per observation, the latest vintage available by then, or a typed empty series.
- The leak detector is the second line only: it flags an injected-outcome feature (its positive control).
"""
from cpe.pointintime.leak import LeakReport, brier, detect_leak
from cpe.pointintime.store import AsOfReader, AsOfSeries, FeatureRow, PointInTimeStore, Vintage

__all__ = [
    "AsOfReader",
    "AsOfSeries",
    "FeatureRow",
    "LeakReport",
    "PointInTimeStore",
    "Vintage",
    "brier",
    "detect_leak",
]
