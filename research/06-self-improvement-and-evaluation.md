# 06 Self-improvement and experimental evaluation

Entry point for the self-improvement loop (`02/01` §8), anti-reward-hacking controls (`04/03` §4), the
25-year evolution rules (`02/04`) and the method scanner (`02/05` §4). §1–§3 summarise the original; §4 is review.

## 1. The loop (`02/01` §8)

**Proposer** (any model, any time) proposes a versioned artefact (feature extractor, parser, graph template,
exit rule, prompt) with a pre-registered claim and the holdout it should improve. **Promoter** (separate OS
account, deterministic script) evaluates on hash-pinned frozen holdouts listed in the ledger, time-shifted
holdouts, shuffled-label controls and canary events; accepts only if the committed e-process against the
incumbent exceeds 1/α (α = 0.05, one test per artefact) and no control is violated; writes `promotion` or
`rejection` to the ledger; keeps rollback. The loop may never change risk limits, gate state, broker
permissions, evaluation datasets, the ledger or fusion thresholds. Live P&L is never an input.

## 2. Anti-reward-hacking controls (`04/03` §4)

Tests that would fail under hindsight tuning: shuffled-label holdout must show no gain; time-shifted holdout
(challenger trained to T must not beat baseline on events resolved before T − lag); canary events with
fabricated outcomes known only to the promoter; e-process λ from the past only. Promotion only via the
promoter script with pre-registered thresholds and rollback by default.

## 3. Over 25 years (`02/04`)

Core vs shell (§2); every new model walks shadow → proof (≥ 150 resolved events, e ≥ 1/α vs incumbent) →
promotion by the promoter → retirement by the reverse e-process or provider shutdown, with its forecasts kept
forever (§3); permanent pre-registration; an annual α-budget (e.g. 20 primary artefact tests per year) or FDR
control, to be chosen as a core decision; anytime-valid monitoring in both directions (improvement and
degradation); automatic anchored annual report including negative results; reproducibility from ledger,
registry and pinned artefacts; annual restore test on a fresh machine (failure is P0); runbooks, key escrow,
dead-man switch; core changes proposed only as text to the owner. Method scanner (`02/05` §4): arXiv categories,
provider announcements, Saxo and TypeSafe documentation changes, triaged by Jev into method candidates with a
pre-registered test idea; monthly method round; nothing adopted because it is new.

## 4. Review

**How should the system improve without optimising against its own test data?** The package's answer,
proposer/promoter separation with frozen holdouts and controls, is the right shape. Specific weaknesses:

1. **Canary events contaminate the registry unless segregated.** Fabricated outcomes known only to the
   promoter must never enter calibration statistics, e-processes, or the shadow books; and a researcher model
   that forecasts on a canary learns nothing true. REVISION: canaries live in a promoter-only registry
   namespace, are never shown to researcher models as resolved, and are excluded by construction from every
   statistic except the promoter's integrity check.
2. **The promoter runs code the proposer can influence.** A "deterministic script" still imports parsers,
   feature extractors and scoring code; a proposer that can change a parser can change what the promoter sees.
   REVISION: the promoter pins the hash of its entire evaluation environment (code, data, dependencies) per
   decision, evaluates only artefacts delivered as data (model weights, prompt text, parameter files) through a
   fixed interface, and logs the environment hash in the promotion record. Changes to the promoter's own code
   are core changes (owner, external review).
3. **Frozen holdouts are exhausted by repeated use.** Every look at a holdout leaks a bit. With dozens of
   artefacts per year over decades, the frozen sets become training data by selection. REVISION: rolling
   prospective holdouts (events registered after the artefact was proposed are the only confirmatory test;
   frozen historical sets are screening only), plus the reusable-holdout idea (noisy, thresholded answers) if
   historical sets must be reused.
4. **The α-budget is unprincipled as stated.** "α = 0.05 per artefact, at most 20 artefacts per year" caps the
   expected number of false promotions at one per year and ignores dependence between tests. Since every test
   is already an e-process, use what e-values are good at: combine by multiplication across independent
   artefacts, average across dependent ones, or apply e-BH for false-discovery control. Decide once and write it
   into the core.
5. **Time-shifted holdouts need the publication-lag table to exist.** The test "trained to T must not beat
   baseline on events resolved before T − lag" is only meaningful if lag is known per source. This control
   depends on `02/01` §3.2 being populated; until then it is inert.
6. **Degradation monitoring is specified but has no action attached.** The reverse e-process detects a model
   that got worse; what happens then (automatic retirement, weight reduction, owner alert) must be a
   pre-registered rule, or the detection is a report nobody acts on.
7. **The method scanner is an attack surface.** Documents from arXiv and vendor blogs reach a model that
   proposes changes to the system. Treat scanner inputs as untrusted (no instructions followed from them,
   only metadata extracted), and route method candidates through the same promoter path as any artefact.
   The package implies this; make it explicit.
8. **Order of construction.** The loop should be built last (`07/02` §B priority 9), and the package agrees.
   Before it exists, the "self-improvement" requirement is met by humans running the same promoter protocol by
   hand on a quarterly cadence, which also produces the first frozen holdouts.
9. **The restore test is the most valuable longevity control and the cheapest.** Do it from month one: rebuild
   registry state from the ledger on a clean machine. Probe P2 (`01-architecture.md` §3) shows the reference
   code cannot do this yet.
