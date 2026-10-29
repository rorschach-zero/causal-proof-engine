"""Whole-codebase audit, pass 7 (issue #37), at ``c55e4cee65656355850bde32b07059e37d8b523b``: inputs decided as the
ledger persists them.

- Codex 7-2 (PR #82 review comment 4416532454): the registration registry validated an input through its payload
  but kept the caller's objects, so a ``str`` subclass that compares equal to one value while its text is another
  passed the admission checks as the first and was persisted as the second. ``submit_forecast`` with an arm version
  whose text is ``unregistered-version`` but which compares equal to ``FULL-1`` was acknowledged, and every later read
  of the registry refused the ledger (``invalid_record ... wrong_arm_version``). The adjudication registry already
  reads its inputs back through the canonical form (PR #54 review 4353163782); the capability gate had the same gap:
  a capability the owner signed for another environment passed as this gate's, and its intent made every later gate
  read refuse the ledger. Both now decide on the value the ledger persists.

Both tests failed on the pass-7 pin."""
from __future__ import annotations

from pathlib import Path

import pytest

from cpe.canonical import JsonValue, digest_of
from cpe.clock import ManualClock
from cpe.errors import Refusal
from cpe.registration import RegistrationRegistry
from cpe.validation import check_issuance
from tests.test_capability import EVIDENCE, Rig, issue
from tests.test_input_validation import VERSIONS, jev, output
from tests.test_registration import clock as clock, ledger as ledger, registry as registry  # noqa: F401 (fixtures)
from tests.test_registration import day, forecast


class LooksLike(str):
    """A string whose text is one value and which also compares equal to, and hashes as, another."""

    def __new__(cls, text: str, alias: str) -> "LooksLike":
        made = super().__new__(cls, text)
        made.alias = alias
        return made

    alias: str

    def __eq__(self, other: object) -> bool:
        return str.__eq__(self, other) is True or str.__eq__(self.alias, other) is True

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.alias)


def test_codex7_2_a_forecast_is_admitted_as_the_ledger_persists_it(registry: RegistrationRegistry,
                                                                   clock: ManualClock) -> None:
    clock.set(day(21))
    disguised = forecast("E-1")
    object.__setattr__(disguised, "arm_version_id", LooksLike("unregistered-version", "FULL-1"))
    with pytest.raises(Refusal) as refused:
        registry.submit_forecast(disguised)  # at c55e4ce: acknowledged, and every later read refuses the ledger
    assert refused.value.reason == "wrong_arm_version"
    assert registry.state().events  # the ledger stays readable


def test_codex7_2_a_capability_is_checked_as_the_ledger_persists_it(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    elsewhere = issue(rig.epoch(), "elsewhere", environment="env-2")  # signed by the owner for another environment
    object.__setattr__(elsewhere, "environment", LooksLike("env-2", "env-1"))
    assert rig.refused(elsewhere) == "wrong_environment"  # at c55e4ce: acknowledged, then every read refused
    rig.gate.state()
    rig.gate.perform("research")


def test_g1_a_capability_signed_for_other_evidence_does_not_promote(tmp_path: Path) -> None:
    rig = Rig(tmp_path)
    rig.tick()
    other: dict[str, JsonValue] = {"bundle": "not-the-evidence-presented"}
    signed = issue(rig.epoch(), "other-evidence", evidence=other)  # the owner bound another evidence bundle
    object.__setattr__(signed, "evidence_digest", LooksLike(digest_of(other), digest_of(EVIDENCE)))
    assert rig.refused(signed) == "evidence_mismatch"  # at c55e4ce: acknowledged at SIM_READ_ONLY (T-30)
    assert rig.gate.state().level == "RESEARCH_ONLY"


def test_i1_an_issuance_counts_each_provider_as_its_output_names_it() -> None:
    disguised = output("P-A")  # P-A's output, presented as P-B's
    disguised["arm_id"] = disguised["forecast"]["arm_id"] = LooksLike("P-A", "P-B")
    disguised["forecast"]["arm_version_id"] = LooksLike("P-A-1", "P-B-1")
    decision = check_issuance("E-1", VERSIONS, [output("P-A"), disguised, output("P-C")], jev(), slot_id="primary")
    assert decision.status == "rejected"  # at c55e4ce: issuable with two outputs of P-A and none of P-B (T-28, RC-17)
    assert ("duplicate_provider", "P-A") in [(p.reason, p.subject) for p in decision.problems]
