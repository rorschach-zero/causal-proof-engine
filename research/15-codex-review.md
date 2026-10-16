# 15 Independent scientific and engineering review

**Review date:** 2026-10-16. **Scope:** research PR [#1](https://github.com/rorschach-zero/causal-proof-engine/pull/1), fetched head `8b2dba79fe9077df53a96a6b61b1823b80930ee8`. Review branch: `review/codex-20261016`, based on that research head, not `main`.

**REVISION — Recommendation: approve Phase 1 with amendments.** Approve only the offline, synthetic-data measurement apparatus described below, after the owner accepts the blocking amendments. Do not approve the investment engine, a strategy, provider or broker integrations, self-directed promotion, SIM orders, or capital deployment through this review. The existing research is a useful problem inventory, but several statements accepted as mathematically sound are false or insufficiently qualified. Passing its tests does not resolve them.

**REPRODUCED —** The archived v0.2 suite passes 31 tests; reverse-patched v0.1 passes 11; the ten attack outputs reproduce apart from timing; all 71 manifest entries verify. The six foundation probes reproduce. New counterexamples expose invalid fusion outputs, replayable authorization, untrusted timestamps, state changes after failed persistence, and incomplete secret handling. A seeded power study quantifies the proposed test's limited sensitivity. Lean was attempted, but neither proof file compiled in this environment because Mathlib's compiled dependencies were unavailable; the archived positive and negative Lean results remain **PACKAGE-VERIFIED**, not independently reproduced.

**HYPOTHESIS —** CPE could improve disciplined event forecasting and research selection. There is currently no prospective evidence that it identifies future 10x–100x investments before price acceleration, that three providers improve outcomes at equal cost, or that a crisis policy adds economic value. Better milestone forecasts are neither necessary nor sufficient evidence of extraordinary investment returns.

**REVISION — Status convention.** Each labelled paragraph or table row applies its status to the whole associated claim. `REPRODUCED` means executed here; `ESTABLISHED` means a mathematical result or independently inspected primary-source fact, within the stated assumptions; `CONFIRMED-DEFECT` identifies a counterexample or a contradiction; `PACKAGE-VERIFIED` retains the archive's evidence without claiming replication; `UNVERIFIED` marks unresolved facts; `HYPOTHESIS` marks empirical conjectures; `REVISION` marks proposed decisions and acceptance criteria. Numerical targets in REVISION passages are proposed policy, not observed results.

## A. Independent top five concerns and severity

**REVISION — Severity meanings:** P0 blocks approval of the affected scientific or security design; P1 must be resolved before prospective confirmation or integration; P2 improves efficiency or clarity. These severities concern future implementation, not an allegation that the research-only repository has placed orders.

| Rank | Severity / status | Finding and consequence | Required disposition |
|---|---|---|---|
| 1 | P0 — CONFIRMED-DEFECT | The implemented e-process tests a conditional null at every update. The programme's average-skill claim, adaptive event selection and outcome-dependent resolution order do not establish that null. Thirty IDs for one fair outcome give a 50% threshold-crossing probability under an average no-skill null. | Specify the estimand, filtration, clustering and maturation protocol before collecting confirmatory data; §C1 and §D. |
| 2 | P0 — CONFIRMED-DEFECT | Mandatory base-rate flooring can inflate rare probabilities or make an interval empty. The accepted nested-event independence claim is false. The proposed interval score does not score epistemic probability intervals as claimed. | Amend D6, N7 and the corresponding AGENTS requirements before implementation; use coherent priors/shrinkage and explicit interval semantics. |
| 3 | P0 — CONFIRMED-DEFECT | Persistence, gate authority and provenance are not enforced boundaries. Backdating works; failed writes mutate state; authorization can be replayed after demotion; mock transport accepts an excluded instrument; exception context retains authorization. | Trusted admission service, transactional state, separate cloud identities, signed capabilities with epochs, and adversarial acceptance tests; §E. |
| 4 | P1 — UNVERIFIED | No validated discovery funnel links early physical/economic mechanisms to value capture, investable entry prices and retained 10x winners. Missed candidates and Jev rejects can disappear from evaluation. | Prospectively sample the eligible universe and rejected funnel; separately test discovery, milestones, economic translation and exit policies. |
| 5 | P1 — CONFIRMED-DEFECT / UNVERIFIED | The timeline asks for outcomes before they mature; 300–600 events have inadequate power for modest gains under the proposed rule; zero incremental cloud cost and actual Saxo ticket economics are unverified. | Correct horizon dates, use a powered feasibility experiment, separate operating and investment budgets, and leave capital outside CPE. |

## B. What was read and reproduced

**REPRODUCED — Scope of inspection.** Read `AGENTS.md`, `CLAUDE.md`, root documentation/configuration/hooks, `research/README.md`, all revised foundation documents `00`–`14`, and the original archive: German chapters, English review/specification/experiment documents, scorecards, reference Python/TypeScript/prompts/proofs, patch, evidence logs, manifest and imported OpenAPI. Read PR #1's metadata/body and research commit messages. No other reviewer was delegated this audit. The only proposed repository change is this review; executable audit snippets are included as documentary evidence in Appendix 1, not introduced as engine modules.

### B1. Provenance and archive integrity

**REPRODUCED — Actual checkout commands** (repository directory `/workspace/causal-proof-engine`):

```sh
git fetch origin refs/heads/research/claude-handoff:refs/remotes/origin/research/claude-handoff
git switch -c review/codex-20261016 origin/research/claude-handoff
git config core.hooksPath .githooks
git log -1 --format='%H %s'
git diff --numstat main..origin/research/claude-handoff -- research/original
git log --format=%B main..origin/research/claude-handoff
git grep -nEi 'api[_-]?key|bearer |refresh_token|AKIA' -- . ':!research/original'
cd research/original/CPE_Forschungspaket_2026-10-16
sha256sum -c MANIFEST.sha256
```

**REPRODUCED — Results:** head was `8b2dba79fe9077df53a96a6b61b1823b80930ee8`; archive diff against main contains additions only, zero removed lines; eight research commit messages contain no prohibited attribution trailers/session URLs. The prescribed secret-pattern search matched explanatory policy/review text only. There are 73 tracked archive files: 71 manifest-covered files, the manifest, and `IMPORT_NOTE.md`; no archive symlinks. Both archived OpenAPI copies are byte-identical, SHA-256 `ee599512cbea3a198b34af3f60addcd72b381d3521196f93c70ae83185c057c3`, version `0.2.0`, with `/v1/models` and `/v1/systemone`. Manifest: **71 OK, exit 0**.

**UNVERIFIED — Limits:** the original ZIP was not available, so its asserted SHA-256 `dc69e2a7bf903547806f1dca38a2bbdbe04595894ae27d79844632341d986415` and equality of Git files to that ZIP were not independently checked. Nor was the original pre-patch 20-file input package available. A manifest stored beside its files verifies consistency, not provenance against a malicious replacement of both. A pattern search is not a comprehensive secret-history audit. No actual credentials were used in probes.

### B2. Python suites and archived attacks

**REPRODUCED — Environment:** Linux, Python **3.12.14**, NumPy **2.3.5**, SciPy **1.17.0**, HTTPX **0.28.1**, pytest **8.4.2**. The archive's logged Python environment differs; matching results here are not a claim of byte-identical runtime replication. All execution occurred on copies under `/workspace/work/cpe-review`, never in the archive.

**REPRODUCED — Commands.** These use the same paths and commands as the execution, with directory setup consolidated for repeatability. `patch` reconstructs a **16-file source tree**; generated caches are not source files.

```sh
CPE_REPO=/workspace/causal-proof-engine
CPE_WORK=/workspace/work/cpe-review
CPE_PACKAGE="$CPE_REPO/research/original/CPE_Forschungspaket_2026-10-16"
CPE_REF="$CPE_PACKAGE/08_Anhang/Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN"
mkdir -p "$CPE_WORK"
cp -a "$CPE_REF/source_v0_2" "$CPE_WORK/v02"
cp -a "$CPE_REF/source_v0_2" "$CPE_WORK/v01"
cp -a "$CPE_REF/EVIDENZ_LOGS" "$CPE_WORK/evidence"
cp "$CPE_REF/PATCH_v01_to_v02.diff" "$CPE_WORK/PATCH_v01_to_v02.diff"
UV_CACHE_DIR="$CPE_WORK/uv-cache" uv venv "$CPE_WORK/venv"
UV_CACHE_DIR="$CPE_WORK/uv-cache" uv pip install --python "$CPE_WORK/venv/bin/python" \
  numpy==2.3.5 scipy==1.17.0 httpx==0.28.1 pytest==8.4.2
cd "$CPE_WORK/v02"
"$CPE_WORK/venv/bin/python" -m pytest -q
cd "$CPE_WORK/v01"
patch -R -p1 < "$CPE_WORK/PATCH_v01_to_v02.diff"
"$CPE_WORK/venv/bin/python" -m pytest -q
"$CPE_WORK/venv/bin/python" -I "$CPE_WORK/evidence/attack_v01_reproduction.py" \
  "$CPE_WORK/v01" "$CPE_WORK/attack-output"
```

| Check | Status | Actual result |
|---|---|---|
| v0.2 tests | REPRODUCED | `31 passed in 3.32s` |
| Reverse patch and v0.1 tests | REPRODUCED | clean reverse patch; `11 passed in 1.69s` |
| F1 ledger rewrite | REPRODUCED | fully rewritten/rehashed v0.1 chain verifies `True` |
| F2 serialization | REPRODUCED | stored JSON uses spaces, hash uses canonical separators; verification works, but reserialization must use the same canonical bytes |
| F3 hindsight evidence | REPRODUCED | ten hindsight updates, e-value about 3.25, rejection `False`; attack demonstrates API permission, not a rejection at ten observations |
| F4 absorbing zero | REPRODUCED | allowed unit bet produces e-value 0 |
| F5 duplicate outcome | REPRODUCED | twenty copies counted; e-value about 9.6, rejection `False` |
| F6 binary allocation | REPRODUCED | analytical/grid weight 0.025; growth about 0.00211 vs cost 0.002; unconstrained weight 8.8 clamped to 0.99 in the separate extreme case |
| F7 enumeration | REPRODUCED | 14 events, 16,384 worlds; about 0.23 seconds here; timing is hardware-dependent |
| F8 arbitrary feasible distribution | REPRODUCED | FF 0.5, FT 0.3, TT 0.2; feasibility does not identify a unique truth |
| F9 evidence admission | REPRODUCED | HTTP URL plus arbitrary digest accepted by v0.1 |
| F10 instrument admission | REPRODUCED | unknown asset type and implausible fractional amount/price accepted by v0.1 |

**ESTABLISHED — Qualification:** constant predictable λ is statistically valid; λ = 1 is also allowed by the usual nonnegative-factor argument, but permits absorbing zero and destroys power on some paths. Those are design/power weaknesses, not by themselves invalidity of Ville's inequality. Hindsight, repeated dependent labels and untrusted commitments are the validity threats.

### B3. Lean attempt and limits of formal evidence

**REPRODUCED — Commands:** installed the official Lean 4.35.0 Linux distribution in scratch; `lean --version` returned `Lean (version 4.35.0, x86_64-unknown-linux-gnu, commit eb6cafb7290e8bd5f2937522d8d804f58f02bafc, Release)`. Used the archived Lake manifest without changing its pins:

```sh
cd /workspace/work/cpe-review
curl -fL --retry 2 --max-time 180 -o lean.tar.zst \
  https://github.com/leanprover/lean4/releases/download/v4.35.0/lean-4.35.0-linux.tar.zst
tar --zstd -xf lean.tar.zst
./lean-4.35.0-linux/bin/lean --version
cd v02/proofs
PATH=/workspace/work/cpe-review/lean-4.35.0-linux/bin:$PATH \
  XDG_CACHE_HOME=/workspace/work/cpe-review/cache lake exe cache get
PATH=/workspace/work/cpe-review/lean-4.35.0-linux/bin:$PATH lake env lean BetThreshold.lean
PATH=/workspace/work/cpe-review/lean-4.35.0-linux/bin:$PATH lake env lean RiskBudget.lean
```

**REPRODUCED — Failure:** pinned Git dependencies materialized, including Mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`. Cache requests to `https://cache.mathlib.org/mathlib4-master` returned `CONNECT tunnel failed, response 403`; the repetitive download attempt was interrupted. Both direct proof commands returned exit 1, `unknown module prefix 'Mathlib'`. This is an environment/dependency failure, not a mathematical refutation. No cache-routing bypass was attempted; a full Mathlib source build was not completed.

**PACKAGE-VERIFIED / UNVERIFIED —** The archived log reports successful compilation and a failing false-threshold negative control. Neither is independently established here; no negative-control success is claimed. Reading the ten lemmas confirms that they express conditional algebra. In particular, `eprocess_factor_nonneg` proves factor nonnegativity, not the conditional expectation inequality, predictability, Ville's theorem or validity of event collection. The call-payoff lemmas omit operational exercise/assignment, financing and execution assumptions. They cannot certify a broker position merely from its asset label.

### B4. Reproduction of foundation probes and additional counterexamples

**REPRODUCED —** Executed `python -I /workspace/work/cpe-review/probes.py /workspace/work/cpe-review/v02` using the scratch venv. Appendix 1 contains the exact executable script and extraction command. It uses synthetic credentials and mocked HTTP only.

| Probe | Status | Result / interpretation |
|---|---|---|
| P1 late YES | REPRODUCED | A late resolution is `resolved_yes`. Real defect: no occurrence-time evidence is required. Disagree with unconditional R4/N11: an on-time occurrence learned late can correctly be YES. |
| P2 restart | REPRODUCED | New registry on existing ledger has zero events. |
| P3 predicate lint | REPRODUCED | `potentially excellent` passes. No machine-checkable predicate contract exists. |
| P4 fusion weights | REPRODUCED | Exactly orthogonal errors with SD ratio 0.02:0.30:0.30 get weights 1/3 each; covariance weights are 0.991189, 0.004405, 0.004405. Different fixture, same defect. |
| P5 gate | REPRODUCED | Constructing `Gate(SIM_EXECUTION)` passes the precheck gate. |
| P6 all-loss scenario | REPRODUCED | `R=[[-1]], Q=[[1]]` yields weight 0. Correct edge behavior; not a portfolio guarantee. |
| Additional registry failures | CONFIRMED-DEFECT | An event and forecast dated in 2020 are accepted today; a 64-character non-hex reasoning digest passes; NO is accepted before the deadline for an eventually-by-deadline predicate; failed append leaves a phantom registered event. |
| Fusion validation | CONFIRMED-DEFECT | NaN intervals, reversed [0.8,0.2], and [1.2,1.3] all yield `forecast`. Three identical constant error histories yield `effective_models=3`; varying identical errors yield 1.25 under 0.30 shrinkage. |
| Anchoring | CONFIRMED-DEFECT | Edit and rehash a suffix after the last anchor: verification passes. The implementation correctly verifies the anchored prefix; the roadmap's stronger “any byte change” promise is false. |
| Gate replay | CONFIRMED-DEFECT | Reusing the same valid promotion after demotion succeeds; the API also accepts a caller-chosen signing key. No durable epoch, expiry or trusted key registry exists. |
| Payload boundary | CONFIRMED-DEFECT | Excluded `Cfd` with amount −1 reaches mocked transport through `sim_precheck`; builder accepts a NaN price and 11 units when lot size is 10. The latter checks minimum size, not lot divisibility. |
| Error boundary | CONFIRMED-DEFECT | `raise ... from None` hides traceback chaining but leaves `__context__.request.headers` containing the synthetic authorization header. The “never propagates request objects” claim is too strong. |
| Sequential application | CONFIRMED-DEFECT | Thirty IDs sharing one fair binary outcome cross 20 with probability 0.5 under an average no-skill null: positive path e = 475.098608, negative path e = 1. A balanced +0.5 then −0.5 stream rejects through its running maximum. These violate the strong conditional null; they do not refute its theorem. |

### B5. Required P0 findings table

| Original finding | v0.1 real? | v0.2 disposition | Level actually demonstrated |
|---|---|---|---|
| P0-SCI-01 forecast object | CONFIRMED-DEFECT: free text and no prospective registry contract | Partial: richer metadata and ID checks; backdating, vague grammar, occurrence-time and replay defects remain | Demo validation only; no trusted prospective system |
| P0-SCI-02 causality | CONFIRMED-DEFECT: logical implication is not an intervention | REVISION: narrative/mechanism split is useful, identification labels do not identify effects | Design taxonomy, not demonstrated causal inference |
| P0-ARCH-01 mandatory models/Jev | CONFIRMED-DEFECT: providers absent, Jev sketch disconnected | Partial: presence checks and a mocked Jev adapter exist; no full provider workflow or independent benefit | Demo mechanics; four-component research is UNVERIFIED |
| P0-BRKR-01 broker boundary | CONFIRMED-DEFECT: no authority boundary/readback | Partial: whitelist and local gate checks; direct construction, payload bypass, replay and secret issues remain | Advisory demo; no deployed isolation or authenticated Saxo validation |
| P0-STAT-01 prospective test | CONFIRMED-DEFECT: update takes outcome and forecasts together | Partial: default λ uses past values and IDs are protected in memory; trusted admission, semantic duplicates, filtration, resolution selection and restart remain open | Mathematical construction conditional on assumptions; demo API does not enforce them |

## C. Eight independent responses to `10-adversarial-review.md`

### C1. Mathematical foundation — partly agree; several accepted claims need correction

**ESTABLISHED — Sound core.** A finite-world probability polytope with nonnegative masses, normalization, marginal interval constraints and genuine logical implications is coherent when feasible. Linear objectives attain extrema at vertices of a nonempty compact polytope. For fixed portfolio weights, expected log wealth is linear in the scenario probabilities, so minimizing over all vertices of the specified polytope is sufficient. A worst case at the lower binary success-probability bound follows when the success payoff exceeds failure. None of these facts establish that the real distribution belongs to the set.

**CONFIRMED-DEFECT — Nested-event chain rule, original `03/01` §4.** If E ⊆ D ⊆ C and P(D), P(C) > 0, then

\[
P(E\mid D)P(D\mid C)P(C)
=\frac{P(E)}{P(D)}\frac{P(D)}{P(C)}P(C)=P(E).
\]

No independence assumption is needed. With probabilities 0.01, 0.10 and 0.50 the product is exactly 0.01. The ban on multiplying *marginals* is sensible; this conditional identity is not that operation. For nonnested sequences use the full chain rule, retaining the relevant conditioning history unless a conditional-independence assumption is justified. Eliciting each link with only one parent can silently discard relevant conditioning. Bayesian networks themselves use conditional factorization, contrary to the archive's claim that they avoid multiplication by construction.

**CONFIRMED-DEFECT — Base-rate floor, D6/AGENTS §2.7.** A population rate is not a lower bound on every member's probability. Evidence of imminent bankruptcy may legitimately make an individual less likely than its cohort to achieve 10x. Replacing a lower bound by `max(lower, base_rate)` changes [0.001,0.01] with base rate 0.02 into invalid [0.02,0.01]. Raising the upper bound as well would repair order but invent support. Flooring point forecasts also destroys the interpretation of calibration and proper scoring. A decomposition is not automatically calibrated: multiplying elicited links can compound selection error, and interval endpoints need compatible joint assumptions.

**REVISION — D6:** use cohort data as a prior or hierarchical shrinkage target, with explicit reference-class selection and parameter uncertainty. For binomial cohort data a declared Beta prior produces Beta(a+s,b+n−s); a new candidate still needs a defensible likelihood/transport model. Without credible cohorts, output a rank and an uncertainty statement, not a numerically floored rare probability. The ban on direct sub-5% narrative elicitation is a prudent workflow constraint, not a statistical theorem. Do not round genuinely estimated small probabilities to 0.05 increments. Distinguish 10x business growth, equity total return, peak tradable return and held terminal return; dilution, financing, valuation and FX separate them.

**CONFIRMED-DEFECT — Fusion.** Correlation-only weighting ignores error scale. Covariance-only R8/N10 is an incomplete repair when errors are biased. For errors e and convex weights w, pooled Brier risk is

\[
E[(w^Te)^2]=w^TE[ee^T]w=w^T(\operatorname{Cov}(e)+\mu\mu^T)w.
\]

Constant but biased errors have zero covariance. Optimize a regularized proper-score objective on a strictly earlier calibration set, constrained to the simplex; use equal weights until it beats a frozen equal-weight control prospectively. A negative unconstrained weight is a reason to solve the constrained problem, not evidence that equal weights are the optimal constrained solution. Retain the mandated three providers and Jev; this recommendation changes pooling, not membership.

**ESTABLISHED / CONFIRMED-DEFECT —** The inverse-variance-style `n_eff` is a diagnostic of a chosen matrix, not a count of independent scientific views. With m = 3 identical variable error series and shrinkage δ = 0.30, equal weighting gives `n_eff = 3/(3−2δ) = 1.25`. For constant duplicate histories the NaN-to-zero correlation repair reports 3. Error correlation also contains the shared outcome term −Y and cannot by itself identify shared training or omitted mechanisms. A threshold such as `n_eff > 1.5` must not certify independence or gate capital.

**CONFIRMED-DEFECT — Interval semantics and N7.** Convex pooling preserves containment of a common p *if every input interval contains p*. That is a deterministic conditional fact, not marginal or conditional statistical coverage. Three separately 95%-covering intervals need not jointly cover with probability 95%. An event resolves to Y∈{0,1}, not to its latent propensity p; testing whether Y lies inside a narrow probability interval is wrong. Scoring its midpoint properly scores the midpoint forecast, not the honesty of its width. The usual Winkler interval score elicits predictive quantiles of an outcome; it does not validate an epistemic interval for a Bernoulli parameter from one realization. [Gneiting and Raftery's proper-scoring framework](https://stat.uw.edu/research/tech-reports/strictly-proper-scoring-rules-prediction-and-estimation) supports the distinction. Do not invoke conformal coverage without specifying its target and exchangeability assumptions.

**REVISION — N7/R7:** commit an explicit point probability for Brier/log scoring and separately state what the interval means: ambiguity set, confidence interval for an exchangeable cohort rate, or posterior credible interval under a model. Report interval width and sensitivity without claiming unearned coverage. Quantile scores are appropriate for separately elicited predictive return quantiles with declared horizons. Calibrate cohort intervals on repeated independent/cluster-adjusted observations. A baseline-imputed abstention is a *policy* score; also report coverage, conditional forecast skill and source-level rejection rates so selective missingness remains visible. Monte Carlo uncertainty must trigger more computation or safe abstention if a decision boundary is unresolved; it cannot simply be ignored under R7.

**CONFIRMED-DEFECT — Credal-net complexity and projection.** Sampling CPT parameters uniformly supplies neither a justified prior nor an outer credal bound. A sampled range is generally an inner approximation of extrema. Exact Bayesian-net inference depends on graph structure/treewidth and CPT size; O(M·edges) does not hold for arbitrary exact marginal inference. Forward state sampling can be cheap per sample but adds outcome simulation error. For a small binary network with separately specified local sets, enumerating all compatible CPT vertex configurations and performing exact inference can recover extrema for appropriate queries. R6's “endpoints per edge” is insufficient without these conditions and can grow exponentially.

**REVISION — D2/R6:** start with C and a small exact A; defer B until it adds out-of-sample value. Conditional bounds can enter a finite LP as `l P(A) ≤ P(A∩B) ≤ u P(A)`, with zero-conditioning-mass semantics stated. Projection must preserve constraints induced through eliminated nodes; a marginal-only LP is usually a relaxation, not a certificate of the network calculation. For portfolio robustness, minimize over the entire declared Q using an inner LP/separation oracle or exact complete vertices on tiny instances. A sampled subset Q' ⊂ Q overestimates the worst-case objective and is not conservative. Test approximation gaps against exact small instances and reject uncertified decision-critical bounds.

**ESTABLISHED — E-process theorem and GRAPA check.** The default code calls its rule on a copy of past increments before incorporating the current outcome. The first-call spy receives `[]`; the independent vectorized recurrence agrees with the reference trajectory. There is no direct current-outcome dependence in default `grapa_lambda`. Under `E[X_t | F_{t−1}] ≤ 0`, measurable λ_t∈[0,1] makes `M_t=M_{t−1}(1+λ_t X_t)` a nonnegative supermartingale. The GRAPA-like heuristic affects power, not this argument. See [Waudby-Smith and Ramdas](https://arxiv.org/abs/2010.09686) and [Ramdas et al.](https://arxiv.org/abs/2009.03167). A user-supplied closure could nevertheless capture the current label; the API cannot certify measurability.

**CONFIRMED-DEFECT — Application of the theorem.** Trusted clock admission, immutable pre-outcome forecasts, semantic event identity, and a justified filtration are missing. `resolved_at` and `known_at` are caller claims. Resolution order is informative: successful approvals may resolve early, failures at expiry; public outcomes may already be known before their ledger update. Requiring one call per ID does not fix either problem. In the cloned-outcome probe, each individual comparison has mean zero before the common outcome, but after the first revelation the remaining comparisons do not satisfy the conditional null. The 50% crossing probability therefore disproves applying this theorem to an aggregate no-skill claim, not the theorem itself.

**REVISION — D4/R3:** predeclare question batches, resolution windows, common-outcome clusters and weights; distinguish occurrence time, public availability, observation time and adjudication time. Fix calendar/cohort maturation and include all outcomes, including unresolved/VOID treatment, without choosing favorable reveal order. Bet only on information genuinely unavailable at the betting cutoff. Where every-step conditional null is scientifically inappropriate, use a prespecified fixed-horizon, cluster-aware paired analysis of the intended average effect, or derive a valid confidence sequence for that estimand under explicit assumptions. Ledger order alone is inadequate. Require valid-null and invalid-null negative controls, not only IID simulations.

**CONFIRMED-DEFECT — Allocation interpretation.** A fully paid equity can lose 100%; original `03/04`'s illustrative lower return bound of −0.75 is not guaranteed by being fully paid. For a position-level wealth-loss limit of 15%, an unprotected total-loss equity must have weight ≤15%, even if D5's nominal position cap is 20%. The portfolio's cash floor of 10% makes the simultaneous gross ceiling at most 90%. Fractional Kelly 0.5 applied after an optimizer with gross ceiling 100% gives at most 50% investment, before any stricter constraints; it is not an implementation of a 90%-invested policy. Terminal scenario loss is not a path drawdown bound, and sampling away joint bankruptcy risks invalidates a worst-case claim.

**ESTABLISHED / REVISION — Costs and objective:** subtracting `−log(1−c)` is exact only for an appropriately specified multiplicative fee convention. If c is a fixed fraction of initial wealth and w is also relative to initial wealth, wealth is `1−c+wR`, not `(1−c)(1+wR)`. Use actual ticket/lot, spread, FX, commission, taxes and cash accounting, then revalidate after rounding and fills. Independently check finite values, probability normalization, feasibility, loss budgets and solver residuals; solver success is not a certificate. Maximizing robust expected log growth is a defensible survival/compounding objective but does not maximize `P(W_T ≥ 100W_0)`. Compare objectives transparently under the same risk limits; do not tune them to manufacture the north star.

### C2. Committee, Jev and simpler controls — partly agree; equal-budget design is essential

**REVISION — Fair R10 control:** run the same source bundles and eligible items through (i) empirical C, (ii) each single model, (iii) each single model in all three roles, (iv) three providers with equal weights, (v) the proposed fusion, and (vi) a source/rules baseline. Match input information, number of calls/samples, total dollar or token budget and latency constraints. Where those cannot all match, preregister a quality-versus-cost frontier rather than claiming one fair scalar comparison. Choose the “best single model” on development data, not the confirmation set. Sample/rotate role assignment to distinguish provider identity from role skill. Keep single-model arms in evaluation only; production membership remains mandatory under AGENTS unless the owner changes it.

**ESTABLISHED / HYPOTHESIS —** Different providers do not imply independent evidence. Shared training, primary-source omissions, the same Jev gate and common prompt author can dominate model diversity. Conversely, correlated predictions may still improve proper score; literal independence is not a prerequisite for useful pooling. R9's evidence-overlap measures are useful diagnostics, but low textual overlap can be paraphrased shared reasoning. Test incremental forecasts and missing-mechanism detection under controlled source withholding; report source overlap, errors and outcome clusters separately. “Independent reasoning” should mean enforced round-one noncommunication, not an untestable claim about model internals.

**REVISION — Jev as a mandatory primary component:** preserve a Jev record on every eligible candidate and final forecast, with input/schema/model hashes, both polarity outputs where applicable, raw and calibrated scores, routing result, failures, latency and total call cost. Use it for primary-source triage, novelty/duplicate detection, contradiction flags and explicit coverage of the discovery funnel. It must not supply a trade probability or veto scientific novelty without an audited escape route. A failure can hold final issuance while research continues; no silent two-provider fallback.

**CONFIRMED-DEFECT — Selection problem:** evaluating only Jev-approved items estimates neither useful-lead recall nor missed winners. Randomly send a prespecified sample of rejected items to the full research pipeline, with known positive inclusion probability in each source/rejection stratum. Use inverse-probability weighting for funnel-level estimates and independent source-grounded adjudication blinded to the routing decision. Preserve the original decision before review; the audit must not rewrite it. Round-two audits of accepted forecasts (R14) address a different problem and must also retain pre/post predictions.

**ESTABLISHED — External evidence inspected on 2026-10-16:** the [Jev benchmark](https://arxiv.org/abs/2609.37647) reports 37 datasets and 346,009 requests, strong classification performance and task-dependent binary thresholds. Its abstract explicitly does not exclude memorized question-answer pairs. The [coherence study](https://arxiv.org/abs/2609.33209) reports mean complement gap 0.064, CI 0.055–0.072, on 480 pairs from 160 items. These are verified descriptions of published experiments, **not REPRODUCED results here**, and neither is a financial forecasting validation. A coherent model can be confidently wrong; projection fixes algebra, not truth.

**ESTABLISHED / UNVERIFIED —** The [TypeSafe introduction](https://typesafe.ai/blog/introducing-system-one-models-and-jev) states $0.042 per million input tokens and 70–500 ms latency; these remain vendor claims, not measured account economics. Its described reference evaluations include frontier-model judgments, introducing potential shared-judge bias. Archived API schema inspection does not prove service availability, stability or real error handling; no authenticated Jev call occurred. A moving `jev-latest` alias is not an immutable version.

**REVISION — Acceptance:** development thresholds may be calibrated on the first 200 documents, but those documents then cannot validate the chosen thresholds. Confirm on fresh strata with enough independently adjudicated positive leads to bound recall. Proposed triage gate: at matched research spend, a one-sided 95% lower confidence bound for recall difference versus the best frozen cheap control above −5 percentage points, with a prespecified positive efficiency gain; use an equivalence/noninferiority design and cluster-aware sample-size plan. If there are too few positives, conclude insufficient evidence. Keep Jev mandatory but soften its routing authority pending evidence. Correct for comparison selection; do not call a single 200-document exercise validation of rare-winner recall.

### C3. Formal verification priorities — partly agree; specify the boundary before proving it

**REVISION — Priority order for R13's six targets:**

| Priority | Target | Useful proof/check and acceptance boundary |
|---|---|---|
| 1 | Gate safety | Capability transitions, epoch/nonce replay rejection, demotion monotonicity and environment separation against a defined authority model. Pair model proof with deployed IAM/egress and crash tests. No theorem about a Python enum establishes isolation. |
| 2 | Ledger/replay | Canonical serialization, committed-prefix verification and deterministic state derivation; atomic failure behavior and restore. State cryptographic assumptions and trust in the external anchor. Do not claim protection for unanchored suffixes. |
| 3 | Allocation certificate | Independent exact/fixed-point checker for concrete quantities, currencies, costs, lots, cash and full-loss exposures, bound to account-state version. Prove checker soundness before optimizing performance. Relevant only before allocator/integration phases. |
| 4 | LP certificate | Primal/dual feasibility and objective enclosure with exact rationals or validated numerical error bounds; generate inconsistent/singular adversarial cases. Proves the supplied model's bounds only. |
| 5 | E-process/Ville | Worth formalizing after the null, filtration, label timing and cluster policy are settled. Nonnegativity alone is insufficient. Statistical protocol review precedes a large Lean development. |
| 6 | Convex interval containment | Small, useful conditional lemma and a regression target; defer broader coverage claims until interval semantics are fixed. Never market this as empirical coverage. |

**REVISION — Counterargument to dropping all unused lemmas:** small algebra lemmas are legitimate proof-pipeline smoke tests and educational contracts. Keep them clearly categorized if they detect toolchain failures; do not count them as safety coverage or reproduce irrelevant option proofs as pilot evidence. The most valuable first investment is an explicit trusted computing base and executable negative controls. A theorem with premises copied from the desired conclusion is not an acceptance test.

### C4. Leakage and shared bias — agree in direction; add tool and evaluator side channels

**CONFIRMED-DEFECT / REVISION — New leakage path:** a promoter can expose holdout labels without returning labels explicitly. Repeated candidate submissions, pass/fail decisions, detailed failure diagnostics, runtime, cache hits or per-item score deltas reveal information about a fixed test set. A “data-only” artifact may invoke a template expression, parser vulnerability, URL fetch or executable deserializer inside the evaluator. Shared cloud logs, object-store permissions, search indexes and cached embeddings can reconnect otherwise separate principals. Model-provider retention or an owner viewing evaluation output can also contaminate later prompts. Hash-pinning the dataset detects edits, not information flow.

**REVISION — Controls and tests:** immutable versioned submission before future data accrue; resource-limited disposable evaluation runners with no network and no secrets; allowlisted declarative artifact schema; evaluator/scorer separation so submitted artifacts never receive labels; per-principal storage and logs; no pickle or executable template evaluation. Limit feedback and the number of adaptive proposals. Use fresh prospective confirmation cohorts after model selection, split by entity/mechanism and time, and record every failed proposal. Inject harmless exfiltration canaries into inaccessible evaluator-only data and test logs, crashes, telemetry and parser errors. A clean scan of the literal word `Bearer` is inadequate; synthetic secret canaries should test encoded and structured paths too.

**REVISION — Round-one evidence:** prompt/configuration/model identifiers and process IDs document a protocol but do not enforce it. Disable undeclared tools and browsing, isolate providers' temporary workspaces, verify complete batch inclusion and preserve raw responses. Provider knowledge cutoffs are approximate; historical “as-of” prompts cannot erase training knowledge. Prefer genuinely future events. In an owner-started batch, record any selection/editing as a different treatment, not a valid continuation of the blinded arm.

### C5. Self-improvement and multiplicity — disagree with R19 as a blanket replacement

**ESTABLISHED —** A fixed weighted average of valid e-values is valid for the intersection/global null without independence. A product requires suitable independence or sequential conditional-e validity; calling artifacts independent is not enough when they share events, labels, sources or adaptive selection. Neither automatically licenses individual promotions. [Wang and Ramdas's e-BH](https://arxiv.org/abs/2009.02824) controls false discovery rate under its conditions, not the probability of any false promotion. The foundation calls N9 “family-wise control” while offering e-BH: that conflates error criteria.

**REVISION — N9/R19/D12:** keep one primary confirmatory claim with an explicit family/lifetime error budget. For successive high-consequence promotions, a simple allocation such as `α_j = 0.05/[j(j+1)]` has total ≤0.05, provided each test is valid conditionally on the prior selection history. An annual reset gives an annual guarantee, not a 25-year guarantee. Use e-BH only for exploratory discovery lists where FDR is the stated objective, not authorization to change a risk-critical component. More efficient online methods can follow when their conditional validity is derived and tested. The increasing thresholds cost power; report that tradeoff rather than describing multiplicative combination as a free solution.

**ESTABLISHED — Counterargument to “ten arms means ten tests”:** a preregistered claim that FULL beats *every* fixed comparator can use an intersection-union test: all required comparisons must reject their nulls, so no Bonferroni correction is needed merely for that conjunction. Selecting whichever arm looks best, making individual superiority claims, or trying many architectures is different and requires selection/multiplicity control. The number of arms alone does not define the inferential problem.

**CONFIRMED-DEFECT — Learning checks:** the proposed condition that a model trained through T should not beat a baseline on events resolved *before* T−lag is not a leakage test; those events can be legitimate training data. Shuffled-label results are random and may differ from a weak baseline by chance; “must show no gain” without a statistical tolerance is ill-posed. Replace time-shift testing with forbidden-future-information negative controls and honest future cohorts. Report shuffled-label null distributions and compare with prespecified error bounds.

**REVISION — Genuine improvement:** freeze a champion and one challenger at each boundary; archive training/calibration provenance and intended effect; use past data for development only. Evaluate fresh future cohorts on the frozen proper-score/policy objective and resource cost. Promote only after statistical evidence plus invariant/security checks and independent authorization. Preserve knowledge of failures in the research record without feeding held-out answers to the proposer. Do not optimize live P&L; permitted offline economic simulation must use a separately governed public/synthetic dataset, not a backdoor to the broker ledger. Thresholds, risk limits and evaluation rules remain owner-governed. Retiring a model after degradation is a separate preregistered action, not permission to relax gates.

### C6. Survivorship and Design C — partly agree; forward data are necessary but insufficient

**ESTABLISHED —** A forward archive can produce valid prospective milestone cohorts, provided eligibility, observations, failures and missingness are logged. It cannot produce mature three-year 10x labels after one year. A Saxo `/ref` snapshot is a broker-accessible universe, not automatically a complete exchange listing history, survivorship-free return series, or corporate-action database. Monthly snapshots can miss securities that enter and disappear between snapshots. Delisted prices and recoveries need dedicated treatment. A prior built only from scanner-selected companies estimates a selected cohort rate, not the market rate.

**REVISION — N1/Q5/R20/R21:** begin source/universe/candidate recording with the first research ingest, independent of Saxo scheduling. Define the investable universe at each decision time with durable identifiers, listing/eligibility intervals, publication lags, splits, dividends, currency, delisting consideration and bankruptcy recoveries. Archive corrections as new versions. Preserve every eligible scanned item and reason for rejection; audit a random sample of items the scanner never shortlisted. A no-exit shadow book alone cannot recover winners the scanner never saw.

**REVISION — Practical C:** use transparent hierarchical frequency/logistic baselines for short-horizon milestone classes where prospectively usable labels exist. Frozen price/momentum, simple fundamentals and public-consensus comparators test whether the causal narrative adds information beyond cheap alternatives. In years 1–2, call long-horizon outputs rankings without claimed calibrated 10x rates. Free official sources may support specific cohorts; their historical completeness, licensing and revision semantics must be tested source by source. A capped data purchase may be economical if it answers a prerequisite, but no budget or account entitlement is assumed here. Do not silently substitute survivorship-biased free data for a licensed PIT dataset.

**UNVERIFIED —** There is no demonstrated source inventory/yield or complete historical delisting dataset in this handoff. The proposed five source profiles should include SEC filings, clinical-trial/regulatory registries, patent/legal-status records, energy/industrial capacity data, and procurement/institutional records as candidates; choose three only after checking access, licensing, latency, deterministic labelability and independent event-cluster yield. Patents and press releases are leads, not established causal efficacy or shareholder value. No claims about these sources' completeness or licensing have been verified in this review.

### C7. Novelty and early exceptional investments — partly agree; avoid claiming exclusivity

**HYPOTHESIS —** The valuable central claim is a chain: early mechanism discovery → superior prospective milestone prediction → durable value capture by identifiable securities → attractive price-relative expected return → ability to hold/reallocate through drawdowns after costs. Every arrow may fail. A technology can succeed while investors lose through dilution, entry valuation, competition or value accruing to customers/private firms. Causal inference from public data can improve explanation without providing information the market has not already priced.

**ESTABLISHED / REVISION —** Early discovery and causal investing are not novel merely because this programme combines them with LLMs. The *only* novel empirical claim cannot be established without a systematic literature/prior-art review. Institution-level auditability, selective research efficiency and incremental committee value are also testable contributions, even if none is a new statistical method. State the narrow contribution and comparator rather than claiming first-principles discovery as a unique scientific invention. [Bessembinder's stock-return study](https://papers.ssrn.com/sol3/Papers.cfm?abstract_id=2900447) supports the importance of a small minority of exceptional wealth creators; it does not show they are prospectively identifiable or supply the needed three-year 10x base rate.

**REVISION — Make H5 plausible and falsifiable:** map a measurable bottleneck or exogenous change to adoption, margins/cash flow, financing survival, competitive response and shareholder capture. Predeclare the event and affected universe before ticker selection; then add valuation and market-information baselines. Identify an intervention, estimand, assignment mechanism, confounders, overlap and interference assumptions when claiming causality. Natural experiments need a credible comparison design; IV needs relevance and exclusion; dose response alone does not remove confounding. Pretrends/placebos are diagnostics, not proof. Validate identification modules on synthetic known-effect and zero-effect systems and selected real quasi-experiments before claiming causal discovery. Better forecasts by an “identification class” do not prove its graphs true.

**REVISION — H5 measurement:** freeze the external-news/search corpus, query protocol, ingestion delay and definition of “first mention”; count censored/no-mention cases. Add a separately registered price-acceleration rule, evaluated on future data and compared to price-only baselines. A 60-day lead over a narrow media corpus can be an indexing artifact. Require correct mechanism/milestone predictions at useful precision, lead before a frozen acceleration definition, and subsequent economic translation. Price blinding is a useful experimental arm, not proof that prices always lag public science. Measure the chance of early false leads and the cost of waiting, not just lead among eventual winners.

### C8. Gate order and trust — partly agree; move design/power/data governance earlier

**REVISION — Order:** (1) owner resolves statistical targets, source eligibility, cloud/budget and governance contradictions; (2) define temporal semantics, error budget and power before confirmatory registration; (3) build and fault-test the offline measurement kernel with reproducible restore; (4) after separate authorization, establish ingest and complete funnel/universe capture, measure supply and calibrate on development data; (5) freeze models/protocol and run prospective forecasting/discovery comparisons; (6) mature economic cohorts and evaluate counterfactual entry/exit policies; (7) independently review broker isolation and read-only/precheck operations; (8) any SIM execution or live pilot receives its own release/approval. Engineering research can proceed in parallel with waiting for labels, without giving unproven forecasting skill trading authority.

**CONFIRMED-DEFECT — Timeline:** a cohort first registered now cannot have observed three-year returns in year two, or a five-year forward return window in year three. Original `04/04` and the foundation milestones conflict on this. Calendar time starts at cohort entry, not research approval. Overlapping five-year windows are not independent samples. Increasing shadow notional to $100,000 adds no statistical information; five years alone is not an adequate-power guarantee.

**REVISION — Counterargument to rigid gates:** operating SIM read-only and testing a broker state machine can be useful before alpha is established, provided those activities have separate authorization and containment. Conversely, statistical rejection, median lead, `n_eff >1.5`, abstention <40% and VOID <10% are not sufficient to trust an investment policy. Require powered, prespecified practical effect sizes, complete coverage and horizon-matched decision evidence. Failure to reach e≥20 at 300 events is not proof of no useful skill; adopt explicit futility/equivalence criteria. No gate sequence substitutes for defining what each test can establish.

## D. Measurable scientific programme and year-one power

### D1. Independent power experiment

**REPRODUCED — Data-generating process:** for baseline b∈{0.2,0.5}, draw p=b±√δ with equal probability, then independent Y∼Bernoulli(p). Baseline predicts b, challenger predicts the true p; expected Brier improvement is exactly δ. This is a deliberately favorable calibrated challenger and marginally calibrated baseline, not a fitted Design-C model or a forecast of real performance. Run the archived GRAPA recurrence with λ_max=0.5, threshold 20, running maximum, 600 observations, 2,000 replications for each seed 17,29,43. Invalid probabilities (b=0.2, δ=0.05) are excluded. Appendix 1 checks its vectorized recurrence against the reference implementation.

| b | True Brier gain δ | Crossings by n=300 / 6,000 | Crossings by n=600 / 6,000 | Power at 600 |
|---|---:|---:|---:|---:|
| 0.2 | .005 | 0 | 31 | 0.52% |
| 0.2 | .010 | 21 | 1,881 | 31.35% |
| 0.2 | .020 | 1,844 | 5,653 | 94.22% |
| 0.2 | .030 | 4,732 | 5,993 | 99.88% |
| 0.5 | .005 | 0 | 85 | 1.42% |
| 0.5 | .010 | 67 | 1,623 | 27.05% |
| 0.5 | .020 | 1,584 | 4,883 | 81.38% |
| 0.5 | .030 | 3,647 | 5,810 | 96.83% |
| 0.5 | .050 | 5,615 | 5,998 | 99.97% |

**REPRODUCED — Valid-null simulation:** fixed b=.4, c=.6, Y∼Bernoulli(.5), so X=±.2 independently and conditionally mean zero. Crossings: 49/6,000 by 300 and 84/6,000 by 600. These empirical rates below .05 do not prove universal validity. The exact cloned-outcome counterexample in B4 shows why a favorable null simulation is insufficient. At 6,000 replications the largest binomial Monte Carlo standard error is about 0.65 percentage points; no table entry is a precise real-world power estimate.

**REVISION — N8 acceptance:** choose a smallest useful proper-score improvement and the claim's sampling unit before choosing a stopping rule. Publish power under realistic fitted baselines, horizon/sector prevalence, correlated clusters, missingness, abstention and provider drift. Proposed minimum is 80% power at the chosen effect and a one-sided 95% Monte Carlo upper bound on type-I error ≤.06 in each specified valid-null stress family, with separate demonstrations of cases outside the assumptions. Adjust sample size/test before confirmation if inadequate. Do not change λ or alpha after looking at test outcomes. The present simulation supports roughly δ=.02 at 600 independent observations in its favorable settings; it does not promise that CPE can attain this effect or supply this many independent events.

### D2. Registered experiment contracts

**REVISION — Common contract:** every experiment freezes eligibility, unit/cluster, source/version, hypothesis, primary metric, practical-effect threshold, stopping rule, missing-data policy and comparison-selection rule before test data accrue. Report all arms and failures. Model/threshold selection uses development data; confirmatory data are future and inaccessible to adaptation. Proposed acceptance thresholds below require a power plan; insufficient sample size is an inconclusive result, not success.

| Experiment | Design and primary measurement | Proposed acceptance / failure interpretation |
|---|---|---|
| Causal discovery | Known-effect/zero-effect synthetic structural systems with confounding, hidden common causes and selection; blinded real natural-experiment cases with independently adjudicated identification assumptions. Compare mechanism extraction to sources-only/rules and random mechanisms. | Recover direction/effect interval on identifiable synthetic cases; calibrated false-positive rate on nulls; abstain on nonidentified effects. Real causal claims require an explicit estimand and defensible design, not just a good forecast score. |
| Forecast calibration | Freeze C, individual providers, single-provider-three-role, equal committee and candidate fusion on identical prospective cohorts. Brier primary; bounded/clipped log score secondary with clipping fixed in advance. Report reliability, calibration slope/intercept, prevalence and cluster intervals. | For the primary claim, valid evidence of superiority plus estimated gain at least the prespecified useful threshold; failures to reach a threshold classified with power/CI. Reliability-bin counts and intervals accompany any calibration claim. |
| Jev contribution | Stratified randomized routing of approved and rejected leads; fixed research budget; blinded primary-source labels; equal-cost rules/cheap-model arm. | Recall noninferiority and efficiency gain per C2; discovery yield and downstream forecast loss must include the weighted reject audit. Cohort scarcity means inconclusive. |
| Early discovery | Freeze mechanism and candidate ranking before defined price acceleration; timestamp first public source and first observed ingest; independently maintained media/search benchmark. | Proposed ≥60-day median lead retained only as a descriptive target until a realistic benchmark distribution exists; primary comparison is increased correct early detections at matched false-lead/research cost, with CI excluding zero. |
| Survivorship / missed winners | Monthly evaluation cohorts from a higher-frequency admission/delisting log; random sample of eligible unselected securities; include bankruptcy and no-longer-tradable cases. Fixed 10x threshold, horizon and total-return convention. | Estimate recall@research-budget and recall@portfolio-capacity over the eligible universe, precision, missed-winner rate and discovery-stage losses with sampling weights. No exclusion of failures or “uninteresting” expired theses after outcomes. |
| Investment translation | Matched-entry, executable-price shadow portfolios: frozen candidate strategy, random stratified selection, simple fundamentals, price/momentum, index total return, cash. Same lots, budget, eligible instruments, publication-to-trade lag and costs. | Evaluate terminal wealth, drawdown, expected shortfall, concentration of gains, turnover, probability of loss and uncertainty at the *mature horizon*. Forecast skill alone cannot satisfy this gate. No alpha claim from $1,000 P&L. |
| Counterfactual decisions | Lock entry and subsequent action alternatives when each real/shadow decision occurs: no-exit, fixed profit-taking, threshold trim, fundamental exit, hazard throttle, with explicit cash/re-entry rules. | Paired terminal-wealth/log-wealth and risk differences, reported for all entries; winner-only regret is secondary. Use feasible liquidity/price assumptions and sensitivity intervals. These are policy simulations, not identified effects of trades on market prices. |
| Self-improvement | Frozen champion/challenger; separate past screening and future confirmation; multiple attempts charged to lifetime budget. Adversarial artifact/canary tests before evaluation. | Out-of-sample practical gain under the registered test, no invariant violations, stable resource costs, independent approval. Repeated holdout optimization cannot qualify. |
| Formal/invariant checks | Fault-inject invalid proofs, corrupt/truncated/rehash ledgers, stale/forged certificates, invalid numbers, out-of-order labels, clock rollback, replayed authorization and concurrent requests. | Every specified invalid input rejected at the true authority boundary; replay and restore match valid history. Removal-of-proof-gate ablation uses known-invalid cases; no spontaneous failures in a benign sample is not proof of value or redundancy. |

### D3. Crisis, temporary drawdowns and exceptional compounders

**HYPOTHESIS —** Early stress detection might improve a constrained policy, but a change-point alert is not a calibrated forecast of a crash. Eight familiar crisis episodes provide weak independent evidence, especially if features and thresholds were chosen after seeing them. BOCPD or a hazard model needs a precise event, horizon and base-rate denominator; class imbalance and alert duration matter. False alarms can lose rebound participation and incur FX/spread/tax costs.

**CONFIRMED-DEFECT — D9 semantics:** a deadline miss can be delay rather than permanent thesis failure; automatic liquidation on every NO overstates the predicate's economic meaning. Conversely, a thesis can remain intact while valuation makes the forward return poor, financing risk rises, or appreciation violates portfolio limits. “Never sell an eventual winner” uses unknowable future information and ignores losses from retained failures. A cash-floor increase from 10% to 30% cannot be achieved immediately merely by stopping purchases if cash is initially 10% and nothing pays out or is sold.

**REVISION — Policy contract:** distinguish a hard current risk limit, a target cash allocation reached by future flows, a fundamental terminal falsifier, a temporary milestone delay, valuation/opportunity-cost review and an operational halt. Declare precedence when a compounder's appreciation exceeds a cap. Price drawdown should trigger an evidence/financing/liquidity review, not a mechanical sell or a rule to ignore all price information. A veto on selling thesis-intact holdings must yield to separately approved hard risk constraints; this is an owner decision, not an automatic change in this review.

**REVISION — Experiment:** compare frozen no-exit, original hazard throttle, fundamental exit, partial trim and fixed profit-taking policies on the same entries, including failures. Use vintage indicators; leave one crisis cluster out for development checks; keep final prospective evaluation separate. Predeclare hysteresis/re-entry, alert precision, time under throttle, drawdown avoided, rebound missed, transaction drag and terminal wealth. Evaluate durable compounders and transient winners using labels that were unavailable at decision time. Record decisions on a fixed calendar so analysts cannot choose only embarrassing exits retrospectively.

**REPRODUCED — Tradeoff illustration:** with zero cash return and ignoring costs, selling half at 10x and holding the other half until 100x yields 55x on the original position, versus 100x without selling. That quantifies upside forgone; it does not prove the trim was wrong ex ante, since the retained half could instead collapse. Report both insurance value and opportunity cost. Gains from one celebrated winner cannot erase the full-cohort comparison.

## E. Cloud, Saxo and engineering governance

### E1. Minimal fully cloud-hosted architecture

**REVISION — N12/D8:** replace the Windows-host requirement. No daemon, credential store, scheduled job, GPU or backup depends on the owner's PC. Owner approval and occasional OAuth login may use any browser; they are human control actions against a hosted service. Start with scheduled CPU containers/jobs, a single trusted transactional event-writer, durable object storage and isolated evaluation jobs. Avoid a distributed microservice or Kubernetes programme until measured concurrency/availability needs justify it.

| Boundary | Cloud role and allowed access | Prohibited path / acceptance evidence |
|---|---|---|
| Ingest and researcher | Versioned public-source snapshots; provider-specific credentials scoped to permitted adapters; submit immutable research records | No broker credentials/private account data, no gate writes, no evaluator labels. Probe IAM/egress denial, not just Python imports. |
| Registry/admission | Trusted server receipt clock, schema validation, append transaction, IDs/cluster semantics, immutable blobs | Researcher cannot backdate acceptance, overwrite outcomes or mutate authoritative state. Crash/concurrency/clock tests and recovery transcript. |
| Promoter/evaluator | Separate identity/storage; frozen datasets, offline artifact execution, bounded output to decision service | No broker ledger, no researcher's mutable environment, no network in submitted-artifact runner. Fresh-cohort and leakage controls. |
| Broker/executor, future only | Separately provisioned account/project or strong equivalent boundary; dedicated secret manager and egress allowlist; instrument/account state and signed approvals | No model-provider access, no executing research code, no shared writable volume. External tests show research cannot reach the execution API. |
| Owner/control plane | Independently authenticated signatures and approvals; separate immutable anchor store and monitoring | Research/promoter cannot issue approvals, rewrite anchor history or reset demotion epoch. Two-way restore/rollback tests. |

**REVISION — Durable design:** use a single writer with a transactional store such as SQLite for a small single-instance pilot, exporting canonical versioned JSONL segments and content-addressed source blobs to immutable object storage. SQLite is not inherently append-only; permissions and transaction ownership matter. Use a managed relational store when concurrency requires it. Event commits and state transitions are atomic; rebuild projections deterministically. Include schema migrations, compatibility tests, canonical numeric/timestamp encoding, backup retention, disaster recovery and bounded restore objectives. Proposed initial recovery objective: reproduce the last externally anchored prefix with zero missing committed entries, and document any unanchored interval; test a clean-cloud-account restore quarterly and after schema changes.

**ESTABLISHED / REVISION — Anchors:** a hash chain only detects changes relative to a trusted head. An external anchor protects the committed prefix and detects truncation below that prefix, assuming hash collision resistance and independent retention. It does not prove original truth or trustworthy timestamps, nor protect later unanchored records. Daily owner copies leave an intra-day hindsight window. Require trusted server acceptance before public outcome availability and anchors/receipts for the relevant pre-outcome batches. For stronger independence, use separately controlled timestamping or immutable retention; explicitly model compromise of the cloud administrator. HMAC authenticates only to holders of its secret and gives no public timestamp guarantee.

**REVISION — Gate authority:** use owner signatures verified with a public key; bind authorization to repository/release digest, environment, account pseudonym, capability, evidence digest, monotonically increasing epoch, nonce, expiry and limits. Store consumed authorizations and demotion state durably. An executor that knows an owner HMAC secret can forge owner authorization. A linear enum conflates environment and capability: `SHADOW_LIVE_QUOTES` must not automatically confer earlier SIM execution rights. Model read/precheck/place/cancel/reconcile as explicit capabilities for an explicit environment. A halt denies new risk while preserving safe reconciliation and explicitly authorized cancellation; killing all access may leave resting orders unmanaged. No such service is implemented here.

**REVISION — Secrets:** use managed secret storage/KMS and workload identities with least privilege, encrypted backups and separate audit identities. Rotate/revoke provider and broker tokens independently. Only the adapter that needs a secret can obtain it; untrusted repository code must not share its environment. HTTP status bodies, retry errors, request objects, tracing and crash dumps require redaction and synthetic-canary tests. `raise from None` is not sanitization of all exception inspection. Never put raw account-state events into the shared research ledger. Canonical broker evidence can be kept in a private ledger with minimal public hashes/reconciliation summaries.

### E2. Saxo facts checked and integration requirements still open

**ESTABLISHED — Primary documentation read on 2026-10-16:** [Saxo environments](https://www.developer.saxo/openapi/learn/environments) separates SIM and LIVE URL paths and credentials. Both use `gateway.saxobank.com`, so hostname-only network allowlisting does not separate them; require credential/environment checks and an endpoint/path policy at the controlled adapter. The [SIM account-linking help page](https://openapi.help.saxo/hc/en-us/articles/4416934146449-How-do-I-connect-a-Live-account-to-a-SIM-Demo-account) states that linking a funded live account enables delayed data for available live instruments. That resolves the narrow Q7 *documentation* question, not this owner's entitlement or a successful readback. The [PKCE page](https://www.developer.saxo/openapi/learn/oauth-authorization-code-grant-pkce) describes an authorization-code flow; example token durations are not an unattended-session guarantee.

**ESTABLISHED / CONFIRMED-DEFECT — Retry semantics:** [Saxo order-placement documentation](https://www.developer.saxo/openapi/learn/order-placement) warns that a timeout can leave an order placed and tells callers to reconcile instead of issuing a second request while awaiting the first. Its duplicate-order protection applies within a short window and can be bypassed by changing `x-request-id`. Generating a fresh ID on every retry would therefore undermine that protection. `ExternalReference` is a correlation field, not demonstrated durable server-side idempotency. Do not infer exactly-once execution from either field.

**REVISION — Future acceptance before SIM execution:** persist intent/outbox and certificate before sending; reserve portfolio budget against concurrent orders; bind the decision to fresh account/reference-data versions; track submission-unknown, accepted, partial, filled, rejected, canceled and expired states. On ambiguous transport failure, reconcile by durable identifiers and authoritative broker state; do not retry until duplication is ruled out, otherwise halt for review. Test delayed/duplicated/out-of-order stream events, partial fills, cancellation races, process death between send and receipt, stale quotes, changed lots/currency, expired authorization, token rotation/revocation and clock skew. Zero duplicate intent execution and complete reconciliation are invariants, not merely a 60-day observed absence of incidents.

**UNVERIFIED —** No Saxo token, account, authenticated readback, precheck, order or 72-hour refresh trial was used. The exact precheck reference URL returned an access/rendering error here; its current field schema remains PACKAGE-VERIFIED. Q1, Q3, Q4, Q6 and Q8 still require authorized account/service tests. A cloud-hosted OAuth callback must be registered HTTPS with state/PKCE and secure rotation; whether this account permits sustained unattended sessions remains unknown. Q9 requires owner-specific tax advice before LIVE; holding-period and turnover preferences are not proof of Swiss tax classification. Do not fund or link an account merely to satisfy this review.

### E3. Repository governance and test enforcement

**REPRODUCED —** The review follows the configured owner Git identity and enabled commit hook. No archive or AGENTS changes are proposed. The user's explicit target `research/claude-handoff` takes precedence over AGENTS' default PR-to-main rule; the research PR stays independently reviewable. There are no tracked `.github` workflow files at the reviewed head. The connector returned no PR-triggered workflow runs for that SHA; that API view alone does not prove there were no other historical CI jobs.

**UNVERIFIED / REPRODUCED — Remote enforcement:** ruleset inspection returned HTTP 403 with an upgrade/public-repository requirement. Branch-protection inspection returned 403, “Resource not accessible by integration.” These responses do not establish the complete protection configuration. Required checks/reviewer restrictions are unverified. The review must not label CI green where no applicable CI was run.

**CONFIRMED-DEFECT / REVISION — Local governance is not server enforcement:** `.githooks/commit-msg` covers specific attribution patterns and can be bypassed or omitted in another clone; it is not a general ban on every tool's footer. `.claude/settings.json` configures one tool. Add provider-neutral checks for commit/PR text in CI and read back stored descriptions after every mutation; use owner-reviewed required checks and branch rules where available. Do not turn substantive provenance into forbidden decoration: document sources, commands and review lineage while keeping titles/bodies free of promotional trailers. Owner identity records the repository's chosen policy, not a claim that all prose was manually typed.

**REVISION — Phase-1 enforcement:** pinned direct and transitive dependency locks, hash/release-digest pinning where available, typed code, schema/property tests, deterministic replay, crash and fault injection, reference-versus-independent-checker tests, and a reproducible Lean job including a deliberately false proof. Keep tests outside `research/original`; verify its Git tree and manifest without formatting it. Search full Git history with an appropriate secret scanner before enabling credentials; test all log/telemetry paths with fake canaries. A static no-import check is useful but cannot catch dynamic HTTP, subprocess or shared-volume paths. A dependency manifest pinning one revision while its input ref says `master` requires care: freeze the lock and review any resolution/update diff.

**REVISION — AGENTS amendments needing the owner:** remove mandatory rare base-rate flooring; clarify epistemic interval scoring; replace OS-specific secret storage/Windows hosting with cloud identities and managed secrets; reconcile “never sell thesis-intact” with hard limits and valuation review; distinguish mandatory production components from scientific ablations/HUMAN development data; replace annual error-budget resets with an explicit lifetime claim policy. Keep the hard no-live/no-credentials/no-self-modified-risk boundaries. These are proposed changes only; this review did not edit policy or implement exceptions.

## F. Feasibility of the $1,000 pilot and $4,000 → $400,000 objective

**REVISION — Year-one verdict:** feasible as a narrow prospective research/measurement pilot if the owner supplies a realistic operating budget, source access and time. Not a powered test of investment alpha, a validated 10x selector, or a reason to deploy the $1,000 live. Capital size has almost no bearing on forecast sample size; independently resolving cohorts and paying for reliable data do. Keep the remaining $3,000 outside the system. The review itself authorizes no spending or trading.

**CONFIRMED-DEFECT / UNVERIFIED — D10's zero additional cost:** the fully cloud-hosted requirement needs compute, durable storage, backup, logs, networking, CI/proof builds, data access and secret management. Free allowances might cover a small run, but have not been priced or demonstrated. Existing subscriptions are not universal API credits. Source licensing and human adjudication may dominate Jev's advertised token cost. Record marginal cash, existing subscription costs and owner hours separately; “free tokens” do not make source checking free.

**ESTABLISHED — Access documentation read on 2026-10-16:** [Claude's monthly API-credit page](https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-and-team-plans) describes plan-specific credits and supported API use, including eligibility/expiry conditions. [Codex authentication](https://learn.chatgpt.com/docs/auth) documents headless device authentication, and [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) documents scheduled jobs and advanced ChatGPT-managed account authentication. Therefore an owner-started daily OpenAI batch is not established as the only supported technical route. The docs favor API keys for automation and warn about credential exposure; they do not establish this owner's plan, permitted production use or available capacity. [Gemini CLI quotas](https://geminicli.com/docs/resources/quota-and-pricing/) distinguish account/subscription and API authentication tiers. Verify current terms, model availability, limits and account entitlement before deciding the adapter contract; do not scrape chat UIs or bypass access restrictions.

**REVISION — Budget decision, not a price quote:** distinguish $1,000 *investment capital* from operating expense. If $1,000 is the all-in incremental annual research ceiling, an illustrative allocation is $240 compute/storage, $120 backups/logs/security services, $200 data/evaluation access, $140 incremental model/Jev usage, and $300 contingency. This is a proposed spending envelope, not verified vendor pricing; it excludes already paid subscriptions and uncompensated owner time, which must still be disclosed. If measured costs cannot fit, reduce source families, call volume and model experiments; keep all four mandatory outputs for issued committee forecasts. Do not spend the same $1,000 once on operations and again on investments. Obtain a first-month cost/throughput report before committing a yearly event target.

**REVISION — Realistic milestones:** month 1–2: approved statistical contract, offline restore/fault tests, source profiles and budget; month 3–4 after separate authorization: a development cohort, independent label audit, measured source/cluster yield and Jev calibration; remaining year: frozen prospective cohorts and resource accounting. A target of 300–600 *resolved independent-equivalent* events is contingent on measured supply and maturation, not a task quota. Report event types and clusters, incomplete horizons and provider-version changes. Year-one success is trustworthy measurement plus a powered and interpretable comparison, not merely collecting many correlated IDs or observing a profitable position.

**ESTABLISHED / REVISION — Ticket feasibility:** cash is feasible under the existing caps, so calling all pilot limits mutually infeasible is too strong. Eight positions is a maximum, not a requirement. With a 15% full-loss cap on $1,000, a ticket is at most $150. If one-way minimum commission is c_min and commission must be ≤1% of ticket, feasibility requires `c_min ≤ $1.50`, before spreads, FX, taxes, lot constraints and any stricter portfolio limit. Actual account commissions remain unknown. A two/three-position pilot does not resolve concentration or cost merely by changing the label; higher cash or an owner-approved explicit cost tolerance may be necessary. No relaxation is proposed automatically.

**REPRODUCED — Arithmetic:** $4,000 to $400,000 in ten years requires `100^(1/10)−1 = 58.4893%` annual compounding if all capital is invested initially, ignoring costs/taxes. If $1,000 compounds for ten years and $3,000 is added at the beginning of year two with the same constant rate, solving `1000(1+r)^10 + 3000(1+r)^9 = 400000` gives **64.0786%**. If all $4,000 waits one year, the nine-year rate is **66.8101%**. These deterministic illustrations are not return forecasts; later deployment requires still stronger performance.

**REPRODUCED / CONFIRMED-DEFECT — Cycle-table qualification:** with W=10, L=.3 and exactly three cycles, f=.10 gives 2.048383x, f=.20 gives 11.239424x, f=.30 gives 33.076161x and f=.45 gives 101.520780x. The original inverse table explicitly varies losers from .3 to .5: its first two rows use .5, producing about 3x and 14x. The foundation's single preceding .3 assumption obscures that change, so its reproduction statement needs qualification. Calling a 100% hit rate mathematically “impossible” is wrong: it is the boundary case, economically implausible and fragile to costs. Claiming a 20% 10x hit rate is necessary for 100x is also false in the stated broader design: five 30x/.3x cycles need only about 7.45% under this deterministic equal-weight model. Unequal weights, cash, correlations, stochastic counts, timing, costs and path dependence invalidate reading the table as an achievable portfolio distribution.

**ESTABLISHED / REVISION — Rare-event information:** zero successes among n independent comparable trials gives a one-sided exact 95% upper bound `1−0.05^(1/n)`: 5.8155% at n=50 and 1.4867% at n=200. These bounds concern a stable cohort rate and do not identify a specific firm's latent probability. Hundreds of milestone questions cannot replace hundreds of mature rare-return outcomes. Preserve the $400,000 north star as a documented ambition; report feasible objective distributions and probability of loss only from declared models with sensitivity analysis. No defensible probability of achieving the north star can be inferred from this handoff.

## G. Disposition of every decision and proposed amendment

**REVISION —** The following are recommendations for owner approval; prior texts remain unchanged. “Retain” means retain the decision's constrained intent, not certify its empirical premise.

| Decision | Disposition and required amendment |
|---|---|
| D1 | Retain REVISE/no capital/live blocked. Phase 1 only after blocking amendments; no implementation authorized by this audit. |
| D2 | Amend: C plus small exact A first; B is an experimental challenger. Selecting at 150 resolved events is development, with fresh confirmation afterward; no fixed-count claim of sufficient power. |
| D3 | Amend: current numbers are unvalidated tuning choices. Freeze only after a separate calibration protocol and typed finite-input validation; equal weights default. Remove `n_eff` as evidence of independent research. |
| D4 | Retain predictable bounded betting and a running maximum under the appropriate null; amend estimand, trusted timing, clusters and label maturation. α=.05 and λ_max=.5 are defensible starting policies, not demonstrated optimal choices. |
| D5 | Retain fully paid whitelist/no leverage and capital boundary. Clarify full-loss position cap ≤15%, cash/gross joint limits, mechanism exposures, lots, currency and costs. Separate exposure caps from path drawdown targets. |
| D6 | Blocking amendment: delete mandatory base-rate floor; use coherent priors/shrinkage and declared cohort uncertainty. Preserve caution about direct rare-event elicitation. Rankings alone until data support probabilities. |
| D7 | Retain forecast skill as year-one subject; replace failure-to-reject with powered/inconclusive/futility outcomes. Five-year shadow data do not by themselves certify alpha. |
| D8 | Retain separate principals; enforce them with cloud IAM, storage/egress and control-plane boundaries, not just OS users or modules. |
| D9 | Amend: distinguish thesis delay, permanent failure, valuation review and hard risk limits; cash target versus enforceable floor; explicit partial trim/re-entry controls evaluated on all entries. |
| D10 | Amend: costed cloud operating plan and owner-specific supported authentication. No assumption that subscriptions make scheduling free or require a daily manual batch. |
| D11 | Retain ambition and no yearly-profit promise; correct arithmetic qualifications and cohort clocks; remove logically necessary milestone/20%-hit-rate claims and hindsight “never sell winner” rule. |
| D12 | Retain versioning, replaceability, restore, reports and dead-man controls. Amend lifetime testing budget, signed approval epochs and safe halt/reconciliation behavior; immutable core means reviewed releases, not inability to patch a vulnerability. |
| D13 | Retain broad research horizon and staged asset acceptance; choose a narrow measurable first cohort. Cross-asset narratives do not authorize cross-asset execution or justify expanding initial scope. |

| New question | Resolution |
|---|---|
| N1 | Source inventory first; five candidate profiles, choose three after a yield/labelability/licensing audit; forecast volume and independence measured rather than assumed. |
| N2 | Typed predicate grammar plus occurrence/publication/receipt/adjudication times, units, revisions and identity rules; reject semantically unresolved contracts before registration. |
| N3 | Trusted transactional single writer plus canonical export/immutable blobs initially; crash-safe replay, schema migration and restore; no decorative “append-only SQLite” claim. |
| N4 | Independent prefix anchor and trusted admission receipts; define unanchored exposure and administrator threat. HMAC optional only with a meaningful verifier trust model. |
| N5 | Signed, expiring, environment/account/release-bound capabilities with monotone epoch and consumed nonce; durable demotion; executor uses public-key verification. |
| N6 | Isolated round-one workspaces and source access; complete inclusion and immutable response records; metadata is evidence of controls, not the control itself. |
| N7 | Explicit point probability scored; intervals given a declared target. Reject epistemic Winkler coverage claim and base-rate flooring. |
| N8 | Use §D1 power results as a diagnostic; complete cluster/missingness/fitted-baseline study before confirmation; require a prespecified useful effect and adequate power. |
| N9 | Explicit family-wise/lifetime protection for promotion; exploratory e-BH only under its stated FDR objective. Conjunction of all-comparator claims distinguished from selecting winners. |
| N10 | Proper-score stacking using error second moments or direct held-out loss, with regularization and simplex constraint; equal-weight default, covariance alone insufficient. |
| N11 | YES iff occurrence met the registered deadline, with supporting evidence; late observation allowed under a declared latency window. Early NO only when the predicate makes it logically final; source loss/missingness separately adjudicated. |
| N12 | Fully cloud hosted; no Windows/owner-PC dependency. Independent identities, managed secret storage, reproducible images and clean-cloud restore. |

**REVISION — Disposition of R1–R21 and associated proposals:**

| Items | Amendment / acceptance criterion |
|---|---|
| R1 | Retain replay, add transactional failure/concurrency semantics; no authoritative state change on failed persistence. |
| R2 | Replace MAC replay alone with N5 capability/epoch model; forged, stale, replayed and wrong-environment approval tests all fail closed. |
| R3 | Retain single commitment concept, but ledger order is not the statistical filtration; include cluster/maturation controls and trusted receipt times. |
| R4 | Replace blanket late-YES rejection with N11 temporal semantics; adversarial on-time-occurrence/late-observation and late-occurrence cases graded differently. |
| R5 and R5-prep | Retain typed predicates and identification arguments; measure causal validity separately from forecasting skill; synthetic null/identifiable cases and independently reviewed real designs. |
| R6 | Require complete compatible CPT configurations or certified approximation; LP projection constraints preserved; no assertion of outer bounds from random samples. |
| R7 | Separate ambiguity, model disagreement and numerical uncertainty; numerical uncertainty unresolved at a boundary forces recomputation or abstention. |
| R8 | Replace covariance-only optimization with N10; compare with equal weights on untouched future data. |
| R9 | Retain source/blinding diagnostics; do not certify independence from overlap or `n_eff`. Randomize source/role controls. |
| R10 | Retain single-model-three-role control with matched information and resource accounting; choose strongest comparator before confirmation. |
| R11 | Retain logged immutable batch; permitted supported cloud automation is an alternative, owner influence is a distinct treatment. |
| R12 | Retain development calibration but separate it from validation; 200 documents is a setup target, not evidence of rare-positive recall. |
| R13 | Use priority order in C3; distinguish formal theorem, independent executable checker and deployed boundary verification. |
| R14 | Retain randomized round-two audit and pre/post forecasts; add stratified Jev/scanner-reject audits with known inclusion probabilities. |
| R15 | Retain model/config pinning and tools-off round one; new provider version enters a new cohort/forecaster record. No historical-cutoff guarantee inferred. |
| R16 | Retain private canary namespace; exclude from performance scores and test leakage via logs/cache/artifact execution. |
| R17 | Pin evaluator and isolate artifact execution; data-only schema alone does not prove non-executability or non-exfiltration. |
| R18 | Retain fresh prospective confirmation; embargo overlapping entities/mechanisms and log all proposals/feedback. |
| R19 | Reject blanket replacement of alpha budget; use explicit lifetime promotion protection, optional exploratory e-BH. |
| R20 | Start PIT capture at first authorized research ingest; do not wait for SIM. Add securities missed between snapshots and corporate-action/delisting data. |
| R21 | Retain eligibility sampling, add items never shortlisted and known sampling weights; separate conditional skill from whole-funnel policy performance. |
| Cost model / Kelly / scenario grammar | Retain as later research; exact fee convention, integer lots, full-loss/joint stress and independent post-solve checking required. Fractional Kelly selected under frozen risk objectives. |
| Abstention / degradation / financing event | Retain explicit policies; baseline-imputed abstention reports coverage; degradation actions consume governed evidence; milestone delay is not automatically financing death. |

**REVISION — D3/D4 threshold answer:** their numerical values need not block a synthetic Phase 1 that treats them as configuration fixtures. They do block a claim that an operating system is scientifically validated. Validate finite intervals and complete inputs before thresholds; calibrate Jev/fusion thresholds on development data; freeze and power the test before confirmation. A 0.05 significance level is interpretable only with the right null and comparison family; 0.5 betting cap trades speed for stability. A minimum history of 20 is not justification for reliable covariance estimation under drift and clusters.

## H. Phase-1 acceptance and owner decisions

**REVISION — Amended Phase 1:** build only schemas, temporal/event semantics, a trusted offline admission/replay model, durable append transactions, deterministic resolver contract, synthetic cluster-aware scoring experiments, an offline capability-state model, baseline/equal-weight fusion with complete validation, reproducible CI and restore. Develop the statistical contract before coding the e-process consumer. Defer learned fusion, credal networks, hazard models, allocators, provider clients, broker adapters, self-improvement execution and cloud deployment credentials. Design the cloud boundaries now; deploy/integrate them only in later separately approved work. This reduces scientific uncertainty before expanding infrastructure.

**REVISION — Objective exit criteria:**

1. Owner-approved amendments to D4/D6/N7/N9/N11/N12 and the relevant AGENTS contradictions; declared source eligibility and operating budget.
2. Zero accepted malformed/nonfinite/incoherent mandatory research inputs in the specified property-test domain; no silent input dropping or duplicate provider overwrite.
3. Deterministic replay equals online state after valid histories; injected append failure, process death, concurrent submissions, truncation and clock rollback cannot produce an acknowledged phantom record. Restore reports the last independently anchored prefix and any lost/unanchored window honestly.
4. Backdated submissions cannot become prospective evidence; duplicate semantic outcomes/cluster membership, adjudication latency, early NO, late occurrence and late observation handled by the declared contract.
5. Forged, replayed, expired, wrong-account/environment/release capability records rejected; demotion survives restart. No offline proof is described as deployed network isolation.
6. Statistical simulation report with independent recurrence check, documented null/alternative generators, seeds, clustering/missingness sensitivity and the N8 power/error criteria; negative counterexamples remain in the suite.
7. Reproducible pinned test/typing/Lean CI, including known-false proof rejection and malformed certificate tests. A network/dependency failure is reported as a failure to verify, never a passed proof.
8. Independent review by someone other than the author and owner acceptance of scope. Green local tests alone do not satisfy repository merge policy.

**REVISION — Decisions requiring owner approval:** accept this amended Phase 1 or retain a research-only pause; approve the mathematical/governance corrections; select the source cohorts and useful-effect target; choose a lifetime error policy; define research expense versus investment capital and any paid-data allowance; approve the fully cloud-hosted identity/storage model; decide how hard portfolio limits interact with appreciated compounders and valuation exits; confirm supported provider access and human operational duties. These decisions are concrete prerequisites for later work, not a request to fund, integrate or trade now.

**UNVERIFIED — Outstanding empirical/account prerequisites:** original ZIP provenance; independently successful pinned Lean compilation/negative control; actual provider entitlements and Jev stability; source licensing/completeness/yield; mature rare-return labels; actual Saxo fees/asset availability/PKCE longevity/precheck schema; deployed IAM and secret isolation; owner-specific tax treatment. None is silently waived by the recommendation.

**REVISION — Final recommendation:** approve the amended offline Phase 1 as a scientific measurement project. Reject approval of the present design as a validated investment engine or autonomous improvement/trading system. Preserve the original research and record accepted amendments in subsequent owner-reviewed changes. This review stops here; it implements no investment strategy or broker execution.


## Appendix 1. Executable independent audit evidence

**REPRODUCED —** This script is the independent probe/power/arithmetic harness used for B4, D1 and F. It imports only the scratch reference copy, makes no provider or broker call, and uses mocked HTTP. Values labelled SYNTHETIC are fake test canaries. Extract and execute from the repository root after making the scratch copy/venv in B2:

```sh
python - <<'PY_EXTRACT'
from pathlib import Path
text = Path('research/15-codex-review.md').read_text()
start = text.rindex('<!-- audit-script:start -->')
end = text.index('<!-- audit-script:end -->', start)
block = text[start:end].split('```python\n', 1)[1].rsplit('```', 1)[0]
Path('/workspace/work/cpe-review/probes.py').write_text(block)
PY_EXTRACT
/workspace/work/cpe-review/venv/bin/python -I /workspace/work/cpe-review/probes.py \
  /workspace/work/cpe-review/v02 > /workspace/work/cpe-review/probe-results.json
cat /workspace/work/cpe-review/probe-results.json
```

<!-- audit-script:start -->
```python
"""Independent audit reproductions; no provider/broker calls. Run against scratch v02."""
import json, math, sys, tempfile, warnings
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import numpy as np
sys.path.insert(0, sys.argv[1])
from cpe.ledger import AppendOnlyLedger, _canonical
from cpe.registry import EventSpec, Forecast, ForecastRegistry, Forecaster
from cpe.fusion import ModelInterval, JevTriage, fuse, error_correlation, min_variance_weights
from cpe.eprocess import CommittedEProcess, CommittedForecastPair, grapa_lambda
from cpe.allocation import robust_allocation
from cpe.saxo_sim import Gate, GateState, OwnerAuthorization, sim_precheck, SaxoInstrument, build_precheck_payload, SaxoHttpError
import httpx

out = {}
t = datetime(2020, 1, 1, tzinfo=timezone.utc)
def spec(e):
    return EventSpec(e, 'Revenue exceeds threshold by expiry', 'audited filing',
                     'revenue > 100', t+timedelta(days=1), t+timedelta(days=30), 'v1')
with tempfile.TemporaryDirectory() as d:
    ledger = AppendOnlyLedger(Path(d)/'ledger.jsonl')
    reg = ForecastRegistry(ledger)
    reg.register_event(spec('late'))
    reg.resolve('late', True, t+timedelta(days=40), 'audit', 'late-occurrence')
    out['P1_late_yes'] = reg.status('late').value
    out['P2_restart_events'] = len(ForecastRegistry(ledger)._events)
    EventSpec('vague', 'could be excellent', 'source', 'potentially excellent',
              t+timedelta(days=1), t+timedelta(days=2), 'v1').validate()
    out['P3_vague_accepted'] = True
    reg.register_event(spec('backdated'))
    reg.commit_forecast(Forecast('f', 'backdated', Forecaster.CLAUDE, 'v', .4, .6,
                                t, t, ('e',), 'z'*64))
    out['backdated_forecast_and_nonhex_digest_accepted'] = True
    reg.register_event(spec('early_no'))
    reg.resolve('early_no', False, t+timedelta(days=2), 'audit', 'not-yet')
    out['early_no'] = reg.status('early_no').value
    with patch.object(ledger, 'append', side_effect=OSError('injected disk failure')):
        try: reg.register_event(spec('phantom'))
        except OSError: pass
    out['state_mutated_after_failed_append'] = 'phantom' in reg._events
    anchor = ledger.anchor()
    ledger.append('forecast', {'p': .1})
    rows = [json.loads(x) for x in ledger.path.read_text().splitlines()]
    rows[-1]['payload']['p'] = .99
    rows[-1].pop('entry_hash')
    rows[-1]['entry_hash'] = sha256(_canonical(rows[-1])).hexdigest()
    ledger.path.write_text('\n'.join(json.dumps(x) for x in rows)+'\n')
    out['rehash_unanchored_suffix_passes'] = ledger.verify_against_anchor(anchor)

# Exactly orthogonal, zero-mean columns, with markedly different scales.
z = np.tile(np.array([[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1.]]), (10,1))
errors = z * np.array([.02,.30,.30])
w, _ = min_variance_weights(error_correlation(errors, .3))
out['P4_correlation_weights'] = w.tolist()
cov = np.cov(errors, rowvar=False)
v = np.linalg.solve(cov, np.ones(3)); out['covariance_weights'] = (v/v.sum()).tolist()
Gate(GateState.SIM_EXECUTION).require(GateState.SIM_PRECHECK)
out['P5_constructed_gate_passes'] = True
out['P6_total_loss_weight'] = robust_allocation(np.array([[-1.]]),np.array([[1.]])).weights.tolist()
names = ['claude','openai','gemini']; j = JevTriage(.9,.9,0.)
for tag, low, high in [('nan',float('nan'),float('nan')),('reversed',.8,.2),('over_one',1.2,1.3)]:
    out['fusion_'+tag] = fuse([ModelInterval(n,low,high) for n in names], j, None).decision.value
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    out['constant_duplicate_neff'] = fuse([ModelInterval(n,.4,.6) for n in names],j,np.ones((20,3))).effective_models
out['varying_duplicate_neff'] = fuse([ModelInterval(n,.4,.6) for n in names],j,np.tile(np.arange(20.)[:,None],(1,3))).effective_models
g = Gate(); key=b'audit-fake-key'; a=OwnerAuthorization(GateState.RESEARCH_ONLY,GateState.SIM_READ_ONLY,'bundle',Gate.expected_mac(key,GateState.RESEARCH_ONLY,GateState.SIM_READ_ONLY,'bundle'))
g.promote(a,key); g.demote('test'); g.promote(a,key)
out['old_authorization_replayed'] = g.state.value
sent=[]
class MockClient:
    def __init__(self, *a, **kw): pass
    def __enter__(self): return self
    def __exit__(self,*a): pass
    def post(self,url,**kw):
        sent.append(kw['json'])
        return httpx.Response(200,json={})
with patch('cpe.saxo_sim.httpx.Client', MockClient):
    sim_precheck(Gate(GateState.SIM_PRECHECK), {'AssetType':'Cfd','Amount':-1}, {}, access_token='SYNTHETIC')
out['invalid_precheck_payload_reached_mock_transport'] = sent
class ErrorClient(MockClient):
    def post(self,url,**kw):
        request=httpx.Request('POST',url,headers=kw['headers'])
        raise httpx.ConnectError('injected',request=request)
with patch('cpe.saxo_sim.httpx.Client', ErrorClient):
    try: sim_precheck(Gate(GateState.SIM_PRECHECK),{}, {},access_token='SYNTHETIC_CANARY')
    except SaxoHttpError as e:
        out['exception_context_retains_auth'] = e.__context__.request.headers['Authorization'] == 'Bearer SYNTHETIC_CANARY'
payload,_ = build_precheck_payload(SaxoInstrument(1,'Stock','SYNTHETIC',lot_size=10,tradable=True),11,limit_price=float('nan'),certificate_id='audit')
out['nan_price_and_nonmultiple_lot_accepted'] = math.isnan(payload['OrderPrice']) and payload['Amount']==11

def path(xs):
    ep=CommittedEProcess()
    # Map x = +/- .5 to pb=.25, pc=.75 and binary outcome.
    for i,x in enumerate(xs):
        ep.commit(CommittedForecastPair(str(i),.25,.75,t,t+timedelta(days=1)))
        ep.resolve(str(i),int(x>0),t+timedelta(days=2))
    return ep
plus=path([.5]*30); minus=path([-.5]*30)
out['cloned_one_fair_outcome']={'plus_e':plus.evalue,'minus_e':minus.evalue,'crossing_probability_under_average_null':.5*plus.reject_null(.05)+.5*minus.reject_null(.05)}
ordered=path([.5]*30+[-.5]*30)
out['balanced_positive_first']={'mean_x':0.,'max_e':ordered.max_evalue,'reject':ordered.reject_null(.05)}
seen=[]
ep=CommittedEProcess(lambda_rule=lambda h: (seen.append(h.copy()) or .1))
ep.commit(CommittedForecastPair('first',.25,.75,t,t+timedelta(days=1)))
ep.resolve('first',1,t+timedelta(days=2)); out['lambda_rule_first_history']=seen

# Vectorised GRAPA, checked below against the archived implementation.
def trajectories(xs):
    npaths, nsteps=xs.shape
    sums=np.zeros(npaths); sums2=sums.copy(); wealth=np.ones(npaths); peak=wealth.copy()
    checkpoints={}
    for n in range(nsteps):
        if n<2: lam=np.zeros(npaths)
        else:
            mean=sums/n; var=np.maximum(0,(sums2-sums*sums/n)/(n-1)); den=var+mean*mean
            lam=np.clip(np.divide(mean,den,out=np.zeros(npaths),where=den>0)*n/(n+10),0,.5)
        wealth*=1+lam*xs[:,n]; peak=np.maximum(peak,wealth)
        sums+=xs[:,n]; sums2+=xs[:,n]**2
        if n+1 in (300,600): checkpoints[n+1]=peak.copy()
    return wealth,peak,checkpoints
check=np.random.default_rng(5).choice([-.5,.5],size=(1,80))
assert np.isclose(trajectories(check)[0][0],path(check[0]).evalue,rtol=1e-12)
out['vector_grapa_matches_reference']=True
power=[]
for b in [.2,.5]:
    for delta in [.005,.01,.02,.03,.05]:
        if math.sqrt(delta)>min(b,1-b): continue
        counts={300:0,600:0}
        for seed in [17,29,43]:
            rng=np.random.default_rng(seed)
            p=b+math.sqrt(delta)*rng.choice([-1.,1.],size=(2000,600))
            y=(rng.random(p.shape)<p).astype(float)
            xs=(b-y)**2-(p-y)**2
            for n,peaks in trajectories(xs)[2].items(): counts[n]+=int((peaks>=20).sum())
        power.append({'baseline':b,'expected_brier_gain':delta,'n300_crossings':counts[300],'n600_crossings':counts[600],'replicates':6000})
out['iid_power']=power
counts={300:0,600:0}
for seed in [17,29,43]:
    rng=np.random.default_rng(seed)
    xs=rng.choice([-.2,.2],size=(2000,600))
    for n,peaks in trajectories(xs)[2].items(): counts[n]+=int((peaks>=20).sum())
out['valid_conditional_null_mc']={str(n):{'crossings':v,'replicates':6000} for n,v in counts.items()}
out['arithmetic']={'100x_cagr':100**.1-1,'floor_invalid':[max(.001,.02),.01],
                   'nested_chain':(.01/.1)*(.1/.5)*.5,'zero_success_upper_50':1-.05**(1/50),
                   'zero_success_upper_200':1-.05**(1/200),'sell_half_at_10_then_100':.5*10+.5*100,
                   'three_cycles':{str(f):(10*f+.3*(1-f))**3 for f in [.1,.2,.3,.45]},
                   'mixed_loser_rows':{str(f):(10*f+.5*(1-f))**3 for f in [.1,.2]},
                   'five_cycle_30x_required_hit_rate':(100**.2-.3)/(30-.3),
                   'max_mc_standard_error':math.sqrt(.25/6000),
                   'nine_year_cagr_if_deploy_all_after_year_one':100**(1/9)-1,
                   'one_year_1000_then_3000_at_same_rate_final_400000':None}
# Solve 1000*(1+r)^10 + 3000*(1+r)^9 = 400000, with no added capital beyond 4000.
lo,hi=0.,2.
for _ in range(100):
    mid=(lo+hi)/2
    if 1000*(1+mid)**10+3000*(1+mid)**9<400000: lo=mid
    else: hi=mid
out['arithmetic']['one_year_1000_then_3000_at_same_rate_final_400000']=(lo+hi)/2
print(json.dumps(out,indent=2,allow_nan=False))

```
<!-- audit-script:end -->
