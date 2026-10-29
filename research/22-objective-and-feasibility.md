# 22 Objective and feasibility: 4,000 to 400,000 in ten years (PROPOSED)

Status: `PROPOSED`, 2026-10-29, written on `main` at `69a6cd0` by the coordinator at the owner's request. It
records the owner's objective as stated, puts the arithmetic and the documented comparators next to it, and
proposes what each phase must show and when the project stops. Nothing here changes a specification, a
decision or a roadmap item; every proposal is labelled and goes to the owner (`AGENTS.md` §1, §8). No order, no
broker, no provider is involved.

Sources: issue #3 comment `6508303144` (the objective statement); `15` §A and the arithmetic passage of its
section F; `18` §2, §3 and §6; `07` §1 to §3 and its findings 1 and 2; `12` Phases 1 to 7 with their exit
criteria; `05` §1 (the three model roles and Jev); `19` §2; `21` (the precedents). Labels as in `README.md`.

## 1. The objective, as the owner stated it

`ESTABLISHED` (as a statement; recorded in issue #3). The topmost objective of the Causal Proof Engine is to turn
4,000 into 400,000 over the next ten years. The engine is to do this by recognising causal chains, second- to
sixth-order effects of policy, technology, society and other drivers, earlier than millions of people, and
strictly long-term, not by short-term trading. The three model providers of the architecture (Claude Fable
class, OpenAI Astra class, Gemini Argon class, with Jev as the typed triage) are to achieve this together.

`ESTABLISHED`. The research foundation has always named this objective (`07` §4, "the north-star arithmetic";
`15` §A) and has always labelled its feasibility a hypothesis. This document does not change that label. It
makes the hypothesis testable, phase by phase.

## 2. The arithmetic

`REPRODUCED` (re-derived in the session that wrote this note, 2026-10-29, by the command below; the same three
figures were first reported by the Codex review, `15` section F, PR #2): 100x in ten years is 100^(1/10) − 1 =
58.4893 % compounded per year, if all capital is invested at the start and costs and taxes are ignored. If 1,000
is invested in year one and 3,000 at the start of year two, the constant rate r that solves
1000(1+r)^10 + 3000(1+r)^9 = 400,000 is 64.0786 %. If all 4,000 waits one year, the nine-year rate is
100^(1/9) − 1 = 66.8101 %. Later deployment needs more.

```
$ python3 -c "print(100**0.1-1, 100**(1/9)-1)"
0.5848931924611136 0.6681005372000588
$ python3 -c "
lo,hi=0.0,2.0
for _ in range(200):
    m=(lo+hi)/2; lo,hi=(lo,m) if 1000*(1+m)**10+3000*(1+m)**9>400000 else (m,hi)
print((lo+hi)/2)"
0.6407858...
```

`UNVERIFIED` (figures from general knowledge, not checked against a primary source in this session; the
verification path is the published annual letters and the fund's documented history, to be added to `14` if
the owner wants them verified): long-run documented track records sit far below this. Berkshire
Hathaway, about 20 % per year over five decades. The best public long-only managers over twenty-year windows,
about 25 to 30 %. Renaissance Technologies' Medallion fund, the best documented result, about 66 % gross and 39 %
net of fees over three decades, with hundreds of scientists, proprietary data and a hard capacity limit that
forces it to return capital. The objective's 58.49 % is therefore above the best documented net return and
below the best documented gross return, from a start capital of 4,000, for ten years; since the engine's own
costs are carried outside the capital (§7), the comparison that matters is the net one, and taxes on the
owner's side, which this note does not model, raise the gross return the capital itself must earn.

`HYPOTHESIS`. Long-term, concentrated positions change the shape of the arithmetic but not its demand. A 100x
decade built from multi-year holdings means a handful of positions each of which must multiply several-fold,
and a hit rate on them that venture investors, who see hundreds of companies and lose most bets, do not reach.
`REPRODUCED` (same session, formula f = (100^(1/n) − L) / (W − L) for the winner share f per cycle under the
equal-weight cycle model of `15` section F, with n cycles, winners at W and losers at L): with ten-fold winners
and losers at 0.3, three cycles need 44.76 % winners per cycle and five cycles 22.80 %; the 7.45 % figure that
`07` §7 item 1 quotes belongs to thirty-fold winners over five cycles, a different payoff assumption. Under
none of these assumptions is the table an achievable portfolio distribution once costs, correlation, timing and
path dependence enter (`15` section F).

## 3. What the foundation already says about the gap between forecasting and returns

`ESTABLISHED` (`15` §A, D11; `18` §2): there is no prospective evidence that better event forecasts identify
10x to 100x investments before the price moves, and better forecasts are neither necessary nor sufficient for
such returns. Between "the engine sees a third-order effect early" and "the owner earns from it" stand four
separate questions, each with its own failure mode:

1. Is the effect already priced? A chain that millions can read is in the price; the edge, if any, is in chains
   that are long, structural and outside consensus categories, which is what the Argon and Astra research roles
   in `05` were written for.
2. When does it arrive? A correct chain with a wrong clock loses money or opportunity. `07` §4 records the
   trim-versus-hold trade-off: selling half at 10x and holding the rest to 100x yields 55x; holding everything
   yields 100x or a collapse.
3. How large may the position be? `07` §1 to §3: fractional Kelly on the worst case of the credal interval, a
   gross cap, a per-position cap, a worst-case loss limit and a cash floor. The pilot limits of `07` §3 (1,000
   capital, at most 8 positions, 20 % per position, worst-case loss per position 15 %, cash floor 10 %) bound
   exposure and downside, not upside: 15 % of capital in a position that returns 10x over two years, with the
   rest in cash, is 2.35x on the whole and about 53 % per year within the position, loss and cash limits
   (`REPRODUCED`, same session); the mechanism-concentration limit of `07` §3 (at most 40 % of exposure on one
   first-order mechanism) would require that exposure to be spread over at least three independent mechanisms,
   which changes the sizing and not the point. The limits therefore do not decide the objective; they exist so
   that the first error is survivable.
   What they do decide is how much skill is needed per decision, which §6 asks Phase 5 to derive.
4. Is the chain identifiable at all? `18` §2: the confirmatory claim cannot be about causal truth; it can be
   about forecast skill on a fixed question set. Each link of a multi-order chain multiplies the uncertainty of
   the previous one, and the evidence for a long chain arrives only when its last link resolves.

## 4. What the long-term framing changes

`HYPOTHESIS`, derived from `18` §3 and `21`.

- Evidence arrives slowly. If forecasts resolve in years, the owner cannot wait a decade to learn whether the
  engine has skill. Each long chain must therefore be registered as a sequence of dated intermediate milestones
  with exact detection signals: if the chain holds, this and that must be observable in 6, 12, 18 months. The
  Phase 1 registry already supports this (events with deadlines, time stamps, adjudication against public
  records, `19` §2). Skill is then measured on the links, not only on the end of the chain. This is also how
  the precedents in `21` obtained evidence before their final results: held-out years for weather, intermediate
  problems for mathematics, registered endpoints for the trial.
- Power stays low. `18` §3 F1: once a period-level component exists, the information in the primary test is set
  by the number of independent calendar periods, not by the number of events. A long-horizon design has few
  independent periods per year. The design must count periods honestly and must not promise a verdict earlier
  than its periods allow.
- Independence of the three providers is the whole value of having three. `05` §1 and `21` §"What these
  successes have in common": three models that read the same sources and see each other's drafts produce one
  consensus in three voices. Source-locked, blinded first rounds, merged only after each has committed, are a
  requirement of Phase 4, not an option.
- The baseline is the market, not chance. `21` lesson 6: a forecast that restates the market's implied
  probability is not skill. Every registered forecast needs a market- or consensus-implied comparator recorded at
  registration time, so that "earlier than millions of people" is a measured quantity, not a slogan.

## 5. What each phase must show, and when the project stops

`REVISION` (proposed; the phases and exits are those of `12`, the evidence requirements and stop rules are
new and are for the owner to confirm, amend or reject). The stop rules are deliberately stated before any
result exists, in the sense of `21` lesson 2: a decision rule chosen after the outcome is not a rule.

| Phase (`12`) | Exit already defined | Evidence this document adds | Stop rule (proposed) |
|---|---|---|---|
| 1 measurement apparatus | audit gate passed (issue #37) | none beyond the gate | if no pass is reached by the pass the owner names as last, redesign replay before any Phase 2 work |
| 2 ingest, Jev, Design C, first registered events | ≥ 100 registered events, anchors verified from a second machine | every event carries a market- or consensus-implied comparator at registration; every long chain is registered as dated milestones | if fewer than 100 events can be registered with comparators in 12 months, the question set is not fit for the objective; revise Q before Phase 4 |
| 3 SIM read-only | 7 days of readbacks, token-leak audit | none | as in `20` |
| 4 three-model adapters and fusion | three independent round-1 outputs per event | blinding and source-locking demonstrated by a leak test; reasoning-overlap metric (`12` R9) below a pre-registered ceiling | if the three outputs are not independent by the metric, do not count them as three |
| 5 evaluation, certificates, no orders | 150 resolved events, design selection, independent review | the pre-calibrated fixed-horizon test of `18` §6 on the registered comparator; a skill estimate with its interval; the share of resolved milestones that confirmed their chain; a pre-registered forecast-to-payoff model (§6) evaluated on the same events | two separate rules: (research) if the skill interval excludes any improvement over the comparator, the forecasting claim fails; (investment) if the forecast-to-payoff model, applied under the `07` limits to the resolved events, excludes the compounding the objective needs (§6), stop the investment path and keep the research path |
| 6 promoter and self-improvement | first promotion recorded end to end | none | as in `12` |
| 7 SIM execution | 60 days, zero duplicate orders | realised SIM return against the registered comparator, net of modelled costs | if the SIM return over the registered horizon does not exceed the comparator by the pre-registered margin, no live pilot |
| live pilot (not in `12`; `07` §3 limits) | owner decision | a pre-registered pilot protocol with a hash deposited outside CPE (`21` lesson 2), monthly ruin report (`07` §3) | drawdown beyond the pre-registered limit, or two consecutive annual reviews below the comparator, ends the pilot |

## 6. The effect the objective needs, stated so that Phase 5 can test it

`HYPOTHESIS`, to be made exact in Phase 2 when the question set and the comparator exist. Forecast skill alone
does not identify the return: the same probabilities and the same Brier scores are compatible with different
entry prices, conditional payoffs and holding periods, and therefore with different Kelly allocations and
returns under the same limits; `18` §6 confines its claim to forecast skill on Q and says nothing about
investment value. The investment stop rule therefore needs an explicit, pre-registered forecast-to-payoff
model: for each registered event, the instrument or basket the chain points at, the entry price and date
implied by the forecast's registration time, the payoff conditional on each outcome, the holding period, and
the costs; the model is applied, under the `07` limits, to the events as they resolve, and its realised and
projected compounding is compared with the objective's. Phase 5 should state, before the confirmatory cohort
opens, (a) for the research path, the minimum skill against the comparator that keeps the forecasting claim,
and (b) for the investment path, the mapping and the compounding below which the path is abandoned. The two
rules are kept apart (§5): a forecasting claim can stand while the investment path fails, and the investment
path never counts as evidence of skill. Until then, this document records only the qualitative requirement: a
skill so large that it has no documented precedent, measured so strictly that the owner would believe it
against the base rate, and a payoff mapping validated on the SIM before any capital follows it.

## 7. What this document does not say

It does not say the objective is wrong. It says the objective is a hypothesis with the lowest prior of any
claim in this repository, and that the repository's whole design, pre-registration, anchored time stamps, two
auditors, refusal by default, exists so that the owner learns the truth about it as early and as cheaply as
possible. The money that funds the engine's own operation is not part of the 4,000 (issue #3 comment
`6508303144`); the engine's cost must be carried outside the capital it manages, or it consumes it.

## 8. Decisions for the owner

- OD-22a: confirm the stop rules of §5 as proposed, amend them, or reject them. Without stop rules the
  objective cannot be falsified.
- OD-22b: confirm that every registered event carries a market- or consensus-implied comparator from Phase 2 on.
- OD-22c: confirm that long chains are registered as dated milestones with detection signals.
- OD-22d: confirm that the engine's operating cost is funded outside the managed capital.
- OD-22e: confirm that the investment stop rule rests on a pre-registered forecast-to-payoff model (§6), kept
  apart from the forecasting claim, and that no capital follows the model before it is validated on the SIM.
