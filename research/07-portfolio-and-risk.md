# 07 Portfolio and risk modeling

Entry point for allocation and ruin risk (`03/04`), the crisis hazard model (`03/06`), the north-star arithmetic
(`04/04`), and the asset-class ladder (`02/05`). §1–§5 summarise the original; §6 is review.

## 1. Binary Kelly audit (`03/04` §1) — ESTABLISHED, REPRODUCED

Two-state model: fraction w, success multiple `up`, failure multiple `down`, success probability p;
g(w) = p ln(1 + w(up−1)) + (1−p) ln(1 + w(down−1)); w* = −(pa + (1−p)b)/(ab) with a = up−1, b = down−1.
For up = 10, down = 0.2: w* = 0.025 at p = 0.10, 0.0522 at p = 0.12; positive arithmetic edge iff p > 4/49 ≈
0.0816; full investment at p = 0.12 has E[ln] ≈ −1.14 despite an arithmetic multiple of 1.376. Lesson: the
possibility of 10x alone is irrelevant to position size. Worst case over [p_low, p_high] is at p_low (Lean
`growth_min_at_lower_bound`). v0.1 compared log growth with a cost *fraction*; v0.2 compares with −ln(1−c).

## 2. Scenario-based robust allocation (`03/04` §2–§3, `ref/cpe/allocation.py`)

K joint scenarios, N fully paid instruments, R[k, i] = total-return multiple − 1 after costs, FX and taxes;
credal set Q = finite set of scenario-probability vectors (LP vertices or hand-specified stress vectors).
Objective max_w min_{q∈Q} Σ_k q_k ln(1 + R_k·w); constraints w ≥ 0, Σw ≤ gross cap, w_i ≤ cap_i, worst-scenario
loss ≤ max_loss (hard); then fractional Kelly w ← 0.5·w. Solved in epigraph form with SLSQP; reproduces 0.025 in
the binary case (REPRODUCED in the test suite). Required scenario: "all theses fail together" (financing regime
breaks) with weight from the hazard model; Q includes the Design-C base-rate vertex as a floor. Explicitly a
toy for anything path-dependent, levered or optional, which is why those are outside the pilot.

## 3. Pilot risk limits (`03/04` §4, only if LIVE_CAPPED_1000 is ever enabled)

Whitelist Stock, Etf, Bond, MutualFund, fully paid, tradability from `/ref` readback; gross ≤ 100 % of pilot
capital; position cap 20 % (≤ USD 200); minimum ticket such that commission ≤ 1 % (schedule unknown, Q6);
≤ 8 positions; cash floor 10 %; worst-case loss per position ≤ 15 % of pilot capital; median holding > 12
months, ≤ 24 round trips per year (Swiss professional-trader classification risk, Q9); ≤ 40 % of exposure on
one first-order mechanism; ≤ 50 % in a currency other than CHF/USD; no precheck or order when quote age > 15
minutes or gate heartbeat > 5 minutes. Monthly Monte Carlo ruin report (P(drawdown > 50 % within 5 years),
ES 5 %, P(10x in 10 years) under the model), labelled as model output.

## 4. Crisis hazard model and re-entry policy (`03/06`)

Inputs knowable in real time with lag-table entries: HY OAS level and 3-month change, SLOOS net tightening,
3m–10y curve, NFCI, VIX term structure, breadth, funding stress, earnings-revision breadth, portfolio
refinancing calendar. Model: Bayesian online changepoint detection or logistic hazard on "drawdown > 15 % in
the next 6 months", trained on vintage data, purged walk-forward; output a hazard distribution with a
calibration interval, never "CRASH = YES". Four cases separated (systemic risk before losses; drawdown without
fundamental deterioration; durable thesis impairment; temporary liquidity panic). Actions with hysteresis
(upper/lower bands, 30-day minimum dwell): hazard HIGH → new purchases to zero, cash floor to 30 % via
non-reinvestment and independently thesis-justified exits, **never forced liquidation of thesis-intact
positions**; thesis break (a load-bearing registered event resolves NO or a counter-mechanism event resolves
YES) → sell regardless of price; pure price drawdown → no action, logged for the late-exit audit; re-entry at
half speed for 60 days after the lower band. No price stops; −30 % gap scenarios in the allocator set. H6
backtest episodes: 2000–02, 2007–09, 2011, 2015/16, Q4 2018, 2020, 2022, plus 2024–26 with vintage data.

## 5. North-star arithmetic (`04/04`) — REPRODUCED

100x in ten years = 58.49 % CAGR fully invested from day zero. With equal-weighted cycles, hit rate f, winner
multiple W and loser multiple L, the per-cycle multiple is fW + (1−f)L and the product over cycles must reach
100. Three 3.3-year cycles need 4.64x per cycle: f ≈ 45 % with 10x/0.3x, ≈ 15 % with 30x/0.3x. Five 2-year
cycles need 2.51x: f ≈ 23 % with 10x/0.3x. Conversely, with 10x winners over 3.3-year cycles: f = 10 % → 3x in
ten years (11.8 % CAGR), 20 % → 14x (30.0 %), 30 % → 33x (41.9 %), 45 % → 101x (58.7 %). The package states as
unverified general knowledge that the base rate of any listed stock making 10x in three years is low single-digit
percent and that documented long-run public records are around 20–30 % CAGR. What is therefore **not** a goal:
profit every calendar year, beating the index every year, low drawdown as the main criterion. Milestones:
years 1–2 milestone skill and ≥ 60-day discovery lead; from year 2 rank correlation of 10x candidates with
realised 3-year returns; from year 3 shadow book beats S&P 500 total return over rolling 5-year windows with
≥ 1 realised 10x and a 10x hit rate ≥ 20 % within 3.3 years; always, no sale of a later winner for price reasons.

## 6. Review

1. **The pilot limits are mutually infeasible until Q6 is answered.** USD 1,000, ≤ 8 positions, 20 % cap,
   commission ≤ 1 % of ticket: at a typical minimum commission of a few USD per trade, tickets would need to be
   several hundred USD, so at most 2–4 positions, not 8, and diversification across mechanisms (≤ 40 % per
   mechanism) becomes arithmetic rather than policy. Either the pilot is an operations test with 2–3 positions
   (say so), or the commission rule is relaxed with a stated cost drag. Decide after the SIM `/ref` readback.
2. **Fractional Kelly 0.5 is a convention, not a derivation.** The package says fractional Kelly covers
   "model misspecification beyond the interval" (`03/04` §3). Make that quantitative: run the allocator under
   perturbed inputs (intervals shifted by their historical calibration error) and choose the fraction that keeps
   P(drawdown > 50 % in 5 years) under a pre-registered ceiling. Report the fraction as a derived artefact.
3. **Scenario-set construction is the hard part and is unspecified.** The allocator is only as good as the
   joint scenarios (macro regime × thesis outcomes × financing) and their credal vertices. Who builds them, from
   what, with what dependence structure, and how they are validated against realised joint outcomes is not in
   the package. REVISION: define a scenario grammar (named regime axes, thesis-outcome nodes, financing node),
   generate the joint set deterministically from the credal net's decision projection plus the hazard model,
   and back-test the *scenario coverage* (how often realised outcomes fell outside every scenario).
4. **"Never force-liquidate thesis-intact positions" is a prior with a tail.** It is the right default for a
   100x programme and the package defends it well, but a thesis can stay "intact" by the registered events while
   the firm's financing disappears (the regime case). The thesis-break rule needs a financing-event class
   (covenant breach, failed raise, going-concern note) registered for every `financing_dependent` thesis, so
   that liquidity death is a thesis break, not a price move.
5. **H6 cannot be powered on eight episodes.** The crisis backtest set has ~8 drawdowns; any throttle rule will
   fit them. Treat H6 as exploratory for years, report it with confidence intervals from block bootstrap over
   the full history, and keep the throttle's cost (false alarms) as the primary reported number. The package's
   fallback (remove the throttle, keep thesis-break selling) should be the default until H6 has evidence.
6. **US-centric hazard inputs** (`01-architecture.md` §4 item 6).
7. **Costs enter R_k "supplied by the caller".** FX conversion, commissions, spreads, Swiss stamp duty where
   applicable, and withholding taxes on dividends are each a few tens of basis points to percent; at USD 1,000
   they dominate. The cost model must be a first-class component with its own tests, not a caller convention.
8. **The ruin report is the right instrument; publish its inputs.** P(10x in 10 years) under the model is a
   number the owner will read as a forecast. Always print it with the scenario set hash, the credal vertices and
   the calibration error of the inputs, and never without the always-invested benchmark beside it.
9. **The asset-class ladder is sound.** Five acceptance artefacts per class, Lean loss bound required, stage 4
   (futures, short options, CFDs, FX margin) only by core change. Nothing to add except that stage 1
   (commodity ETCs) needs the roll-cost model *before* shadow, since roll yield can dominate the thesis.

## 7. Amendments after the Codex review (REVISION, 2026-10-16)

Recorded after reconciliation round 1 (`16-reconciliation-matrix.md`); the text above is left as written.

1. **§5 cycle table (RC-21).** The inverse table's first two rows in `04/04` use a 0.5 loser, not 0.3; the
   summary above states 0.3 without the caveat (the mixed losers were flagged in `00-research-inventory.md`
   §5). With 0.3 throughout, f = 0.10 gives 2.05x and f = 0.20 gives 11.2x. "A 10x hit rate ≥ 20 %" is not
   necessary for 100x in the stated design (≈ 7.45 % suffices with five 30x cycles) and is withdrawn as a
   milestone; "100 % hit rate impossible" is a boundary case, implausible rather than impossible. Milestones
   are re-expressed as months after first cohort entry: a cohort registered now has no three-year return in
   year two.
2. **§6 item 1 (RC-27).** "Mutually infeasible" was too strong: cash is always feasible, and eight positions is
   a maximum. The exact condition: with a 15 % full-loss cap a ticket is at most USD 150, so commission ≤ 1 %
   requires a one-way minimum commission ≤ USD 1.50 before spreads, FX and taxes; unknown until Q6.
3. **§3 limits (RC-22).** A fully paid equity can lose 100 %, so the 15 % worst-loss rule caps an unprotected
   position at 15 % of pilot capital regardless of the 20 % nominal cap; gross exposure with a 10 % cash floor
   is at most 90 %; the Kelly fraction belongs inside the constrained objective, not after it.
4. **§4 and §6 item 4 (RC-19).** "Never force-liquidate thesis-intact positions" and "never sell a later winner
   for price reasons" are amended: the second is a hindsight rule; a deadline miss can be delay rather than
   failure; a 30 % cash floor cannot be reached by stopping purchases alone. EventSpecs distinguish
   `terminal-falsifier` from `milestone-deadline`. Precedence: hard current risk limits > terminal falsifier >
   valuation/opportunity review > hazard throttle; price drawdown triggers an evidence, financing and
   liquidity review, never a mechanical sale. How caps treat appreciated compounders is owner decision OD7.
   D9 is evaluated as a policy family by locked counterfactual arms on all entries (no-exit, hazard throttle,
   fundamental-falsifier exit, fixed profit-taking, threshold trim, valuation review).
5. **§1 cost term (RC-23).** −ln(1 − c) is exact only under a multiplicative fee convention; the cost model is a
   component with declared conventions (item 7 above stands).
