# 21 AI-driven scientific advances 2023 to 2026, and what CPE should borrow (NOTE)

Status: `NOTE`, 2026-10-29, written on `main` at `69a6cd0` by the coordinator's research task on the owner's
request ("look at all the scientific advancements because of AI online, in math, physics, biology, as an
inspiration for what we are trying to accomplish"). Documentation only. It changes no specification, no
decision and no roadmap item; where it proposes a practice, the proposal is labelled and goes to the owner.

Sources: the numbered list at the end, with each source's URL and date. Limitation, stated once here and once
in the method section: the page fetcher of the research session could not reach external hosts, so every claim
rests on search-engine extracts of the primary pages, cross-checked between sources, not on full-text reading.
Labels: `ESTABLISHED` (confirmed by the primary source or by two independent reputable sources), `HYPOTHESIS`
(inference of this note), `UNVERIFIED` (could not be confirmed). The three strongest lessons for CPE are
restated in `22-objective-and-feasibility.md` §4.

Research note, 2026-10-29, for the CPE research foundation: AI-enabled advances across six fields, with attention
to *how each was verified*. It proposes no code.

## Method and labels

Each bracketed number [n] points to the source list, which gives the URL and the source's date; dates of events are
also given inline. Labels: **ESTABLISHED** (confirmed by the primary source or by two independent reputable
sources), **HYPOTHESIS** (inference of this note), **UNVERIFIED** (could not be confirmed). Limitation, stated
once: the page fetcher of this session could not reach external hosts, so confirmation rests on search-engine
extracts of the primary pages and cross-checks between sources, not on full-text reading.

## 1. Mathematics

**FunSearch (December 2023).** ESTABLISHED. Google DeepMind (Romera-Paredes et al.) published FunSearch in Nature
on 14 December 2023: a pretrained language model proposes *programs*, and a user-supplied `evaluate` function scores
them and discards failures [10]. It found a cap set of size 512 in dimension 8, larger than previously known, and
raised the lower bound on the cap set capacity [10][11]. Verification: an explicit construction anyone can check.
Human role: choosing the problem and writing the evaluator.

**AlphaGeometry (January 2024) and AlphaProof with AlphaGeometry 2 (July 2024).** ESTABLISHED. AlphaGeometry
(Trinh et al., Nature, 17 January 2024) solved 25 of 30 olympiad geometry problems with a neuro-symbolic prover
trained on synthetic data [6]. At IMO 2024, AlphaProof and AlphaGeometry 2 scored 28 of 42 points, silver-medal
level, announced 25 July 2024; AlphaProof searches for proofs in the Lean proof assistant, so each accepted proof
is checked by Lean's kernel; the problems were translated into formal language by humans first, and both
combinatorics problems went unsolved [4][7]. The method paper appeared in Nature on 12 November 2025 [5].

**IMO 2025 gold level (July 2025).** ESTABLISHED. An advanced Gemini Deep Think scored 35 of 42 (5 of 6 problems)
in natural language and was graded through the IMO's own coordination process; an OpenAI experimental model also
reported 35 of 42 but was not officially entered and was graded outside that process; both were announced around
19 to 21 July 2025 [12][13]. Harmonic's Aristotle produced Lean-checked proofs of 5 of 6 problems from supplied
formal statements [8]; ByteDance's Seed Prover reported an IMO-certified 30 points [9]. UNVERIFIED: a quote
attributed to IMO president Gregor Dolinar that the IMO "cannot validate the methods, including the amount of
compute used or whether there was any human involvement" appears only in secondary reports [13].

**AlphaEvolve (May 2025).** ESTABLISHED. Announced by Google DeepMind on 14 May 2025, AlphaEvolve couples Gemini
models with automated evaluators in an evolutionary loop [14]. Reported results: a 48-multiplication scheme for
4x4 complex-valued matrices (Strassen's 1969 construction gives 49), a lower bound of 593 for the kissing number in
11 dimensions (previously 592), matching the best known result on about 75% of more than 50 open problems and
improving it on about 20%, and a scheduling heuristic recovering 0.7% of Google's fleet compute [14][15]. Caveats:
a human researcher later beat several AlphaEvolve bounds [16], and a February 2026 preprint reports that simple
baselines are competitive with code evolution on such tasks [17].

**Erdős problems (October 2025 to August 2026).** ESTABLISHED. On 18 October 2025 an OpenAI executive claimed GPT-5
had solved ten Erdős problems; the maintainer of erdosproblems.com, Thomas Bloom, called this "a dramatic
misrepresentation": the model had found existing solutions in the literature, and the claim was withdrawn [18].
From January 2026 real resolutions followed: Erdős #728 was solved by GPT-5.2 Pro and formalized in Lean by
Harmonic's Aristotle (write-up, January 2026) [19], and Terence Tao kept a public wiki classifying AI contributions
(data to 30 June 2026) [20]. A Google DeepMind sweep of about 700 open problems found that of 200 candidate
solutions that were adjudicated, 137 were fundamentally flawed and 13 (6.5%) meaningfully correct (January 2026)
[21]. AlphaProof Nexus reported 9 of 353 Erdős problems resolved with Lean proofs (21 May 2026) [22]. On 20 May
2026 OpenAI reported a disproof of Erdős's 1946 unit-distance conjecture, checked by external mathematicians
(Alon, Bloom, Gowers and others) who wrote a companion paper [23][24]; on 1 August 2026 it published ten further
results with Lean certificates, including Erdős #146, #180 and #183 [25]. Quanta (3 August 2026) reports Tao's view
that models mostly pick "low-hanging fruit" [26]. UNVERIFIED: a single third-party GitHub audit reports that the
#146 and #180 certificates rely on added axioms [27].

## 2. Formal verification

**Equational Theories Project.** ESTABLISHED. Tao's crowd-sourced project determined all 22,028,942 implications
between 4,694 equational laws of magmas (37.12% true), first informally in about two months, then fully in Lean
over a further five months; the final report is arXiv:2601.20759 (January 2026) [28]. HYPOTHESIS: most machine
help came from automated provers; the language-model share was not quantified in the sources seen.

**Fermat's Last Theorem.** ESTABLISHED. Kevin Buzzard's EPSRC-funded Lean project at Imperial College runs to
September 2029 [29]. In September 2026 Anthropic reported a complete Lean formalization produced by a multi-agent
Claude system in 11 days: about 13 million lines, roughly 29,500 theorems, only Lean's three standard axioms, and a
comparator check that the final statement matches Mathlib's statement of the theorem [30]. Buzzard compiled the
released code himself and wrote on 4 September 2026 that it "faithfully follows the early literature on the proof
and adds nothing" to the mathematics [31][32]. Verification is the Lean kernel plus a statement comparator plus an
independent expert build; the result is a check of Wiles's proof, not new mathematics.

**AI provers.** ESTABLISHED. DeepSeek-Prover-V2 (30 April 2025) reports 88.9% on miniF2F-test, but at pass@8192,
and 49 of 658 PutnamBench problems [33]. Goedel-Prover-V2 (August 2025) reports 88.0% at pass@32 for a 32B model
and 90.4% with self-correction, and compares against Kimina-Prover (84.0% at pass@32) [34]. Lean checks every
proof, so the per-proof claim is reliable; the headline percentage depends on the sampling budget and on whether
benchmark statements leaked into training.

## 3. Physics: fusion control

ESTABLISHED. The TCV result predates the window: Degrave et al. (Nature, 16 February 2022) trained a reinforcement
learning controller in simulation and ran it on the TCV tokamak [35]; a 2023 follow-up improved shape accuracy
[36]. Within the window, Seo et al. (Nature, 21 February 2024) used a learned model that forecasts tearing
instability up to 300 ms ahead to steer DIII-D plasmas below a tearing-likelihood threshold [37]. Verification:
live discharges on the physical machine. The authors note that more data are needed for other conditions [37].

## 4. Weather and climate

ESTABLISHED. GraphCast (Lam et al., Science, online 14 November 2023) outperformed ECMWF's deterministic HRES on
90% of 1,380 verification targets [38]. GenCast (Nature, 4 December 2024), trained on ERA5 up to 2018 and tested on
2019, beat the ECMWF ensemble on 97.2% of 1,320 targets [39]. ECMWF made its own AI model, AIFS Single,
operational on 25 February 2025, added AIFS ENS on 1 July 2025 and upgraded to AIFS Single v2 on 12 May 2026 [40].
Google DeepMind's cyclone model was used by the US National Hurricane Center from June 2025 [41]; the NHC's 2025
verification report found its ensemble mean slightly better than the official track forecast at 12 to 72 hours
[42]. Verification: scoring against observations on held-out years, then real-time forecasts scored by an
independent agency after the fact.

## 5. Biology and medicine

**AlphaFold.** ESTABLISHED. The 2024 Chemistry Nobel (announced 9 October 2024) went half to David Baker and half
jointly to Demis Hassabis and John Jumper for AlphaFold2 protein structure prediction [1]. AlphaFold 3 (Abramson
et al., Nature, 8 May 2024) extended prediction to complexes with nucleic acids and ligands [2]; inference code
was released in November 2024 [3]. UNVERIFIED in this session: that
AlphaFold2's accuracy was first shown in the blind CASP14 assessment of 2020 (from memory; the Nobel background
document [1] is the place to confirm it).

**AI co-scientist.** ESTABLISHED. Google's multi-agent Gemini system (arXiv, 26 February 2025) [43] was given a
question the Penadés lab had answered but not published; its top hypothesis matched the lab's finding that
cf-PICIs hijack tails of diverse phages [44], later published in Cell (2025) [45]. The same report describes
drug-repurposing candidates for acute myeloid leukaemia confirmed in cell lines and liver-fibrosis targets tested
in organoids [43]. Verification: prior and new wet-lab results; one retrospective match is weak
evidence of discovery ability.

**Antibiotics and clinical trials.** ESTABLISHED. Wong et al. (Nature, 20 December 2023) used explainable deep
learning to identify a structural class active against MRSA, validated in two mouse models [46]. Rentosertib, a
TNIK inhibitor that Insilico Medicine reports was found and designed with generative AI, completed a randomized,
placebo-controlled phase 2a trial (71 patients, registered as NCT05938920; Nature Medicine, 3 June 2025); the
primary endpoint was safety and the efficacy signal was modest with wide intervals [47].

**2026.** ESTABLISHED that it was announced; UNVERIFIED as to significance. On 23 September 2026 Anthropic reported
that about 950 Claude agents, over 21 hours, flagged a previously uncharacterized phage enzyme system (ART);
Anthropic states it does not yet know what the system does, and outside experts quoted by Bloomberg were cautious
[48][49].

## 6. Chemistry and materials

ESTABLISHED. GNoME (Merchant et al., Nature, 29 November 2023) reported 2.2 million structures below the known
convex hull, about 381,000 new stable materials, and 736 already independently realized [50]. The companion A-Lab
paper reported 36 of 57 targets synthesized in 17 days [51]. Both drew criticism: Leeman, Schoop and colleagues
(PRX Energy, 2024) argued that about two-thirds of A-Lab's successes were likely known, disordered versions of the
predicted ordered compounds [52]; Cheetham and Seshadri (Chemistry of Materials, April 2024) found "scant
evidence" of compounds that are novel, credible and useful in a random sample of GNoME entries [53].

## 7. Forecasting itself

ESTABLISHED. ForecastBench scores forecasts only on questions that resolve after submission. In 2024 superforecasters
scored a Brier of 0.093 against 0.111 for the best model [54]; by September 2026 the Forecasting Research Institute
reported top AI systems statistically indistinguishable from superforecasters, with overlapping intervals and a
superforecaster baseline last elicited in 2024 [55]. Good Judgment disputes the design [56]. UNVERIFIED: the outcome
of the October 2026 rematch; no result was found.

## What these successes have in common

HYPOTHESIS (synthesis of sections 1 to 7). Six features recur.

1. **A verifiable objective.** Cap set size, multiplication count, kissing configuration, Lean theorem, Brier score
   on observed weather, IMO marks. Where the objective was a proxy (DFT stability for GNoME), the claim was
   contested [50][53].
2. **A verifier independent of the generator.** Lean's kernel, IMO coordinators, ECMWF and the NHC scoring a
   vendor's model, a wet lab, Buzzard building the code himself. Self-graded results (OpenAI at IMO 2025, GPT-5 on
   Erdős) were the ones disputed [13][18].
3. **Closed-loop evaluation on held-out or future data.** GenCast trained to 2018 and tested on 2019 [39]; NHC
   scored a full live season [42]; IMO problems are new each year; ForecastBench uses only unresolved questions [54].
4. **Massive search with cheap checking.** FunSearch, AlphaEvolve, provers at pass@8192. The checker makes the
   search safe; without it errors dominate (6.5% meaningfully correct in the DeepMind Erdős sweep [21]).
5. **Formal methods where available.** Lean converted contested natural-language claims (Erdős #728, FLT) into
   claims anyone can recheck [19][30]. A comparator on the *statement* matters as much as the proof [30].
6. **Pre-registration or time stamps.** The rentosertib trial was registered before results [47]; operational
   forecasts are archived before verification [40][42]; IMO solutions are produced inside a fixed window.

## Lessons for CPE

HYPOTHESIS throughout; the mapping is this note's inference against `research/README.md`, `research/12-roadmap.md`
and `research/19-phase1-handoff.md` sections 1 and 2.

**Where CPE already matches the precedents.**
- *Verifiable objective*: an externally fixed question set Q forecast exhaustively, scored by a pre-calibrated
  fixed-horizon test (handoff §2, OD11 (b)), is the analogue of a fixed benchmark scored by a fixed metric.
- *Future-only evaluation*: the confirmatory cohort is disjoint from the Phase 4 design and burn-in cohort; the
  deterministic rule that selects the numerical parameters is anchored before the design cohort is measured,
  and the parameters themselves are then fixed from that cohort, before the confirmatory cohort opens (handoff
  §2). This is GenCast's train/test split and ForecastBench's unresolved-question rule.
- *Time stamps*: the append-only ledger with anchors and four timestamps mirrors operational forecast archives.
- *Formal methods*: Lean lemmas on a pinned toolchain mirror the kernel check; the FLT case shows CPE also needs a
  statement check, that each Lean statement says what the specification means.
- *Independent verifier*: the two-auditor gate mirrors independent grading.
- *Refusal by default*: RESEARCH_ONLY gating, RE_RESEARCH on missing input and a blocked LIVE state mirror
  ECMWF running AIFS alongside its physics model rather than replacing it [40].

**Where CPE is weaker.**
- *Signal*: weather has 1,320 targets scored daily; CPE's roadmap needs about 100 to 150 resolved events before
  evaluation (roadmap Phases 2 and 5). Even ForecastBench, with far more questions, cannot separate AI from
  superforecasters [55]. Low power is the normal state, not an exception.
- *Adversarial and non-stationary target*: weather does not react to forecasts; markets do. A held-out year in
  finance does not certify the next year.
- *No replication*: a wet lab can rerun an assay; history has one realized path. The nearest substitute is replay
  of the ledger by a second party, which checks bookkeeping, not skill.
- *Verifier fallibility*: adjudication against public records involves interpretation, revision and late
  publication; Lean's kernel does not. Lean lemmas certify the statistics, not that the world lies in the
  validity class 𝓛, which handoff §2 already concedes is unprovable. This is the GNoME pattern: a rigorous check of a
  proxy.
- *Correlated auditors*: two language-model reviewers share training data and failure modes; IMO coordinators,
  wet labs and the NHC do not share the generator's.
- *Survivorship and look-ahead*: finance data are revised and delisted names vanish, which is why CPE needs
  point-in-time universes and candidate logs.

**Practices to borrow.**
1. *Future-only confirmatory evaluation*: no confirmatory question whose outcome is knowable at registration; keep
   reporting the burn-in separately, as ForecastBench separates resolved questions.
2. *External pre-registration*: in addition to the internal ledger, deposit the confirmatory protocol and its hash
   with a third-party registry, as trials use ClinicalTrials.gov [47].
3. *Public time stamping*: anchor ledger heads to a public, independently operated log, so that an outsider can
   date every forecast without trusting the owner.
4. *An independent, non-LLM verifier*: at least one human statistician or outside forecaster group scores the
   confirmatory cohort from the raw ledger, like IMO coordinators or the NHC.
5. *Second-party replication*: publish the resolver, the ledger export and the scoring code, so a second party can
   recompute every score, as Buzzard rebuilt the FLT proof [31].
6. *Denominators and baselines*: log every arm and attempt (CPE's S_max), and score against a consensus or
   market-implied baseline, so that "literature rediscovery" in finance (restating the market) is not counted as
   skill [18][21].
7. *Statement audits for Lean*: pair each kept lemma with a reviewed natural-language statement and a test that
   the code calls the lemma's hypothesis as stated, following the FLT comparator [30].

## Sources

Dates are the source's publication date as shown in the search results; "accessed 2026-10-29" applies to all.

1. NobelPrize.org, press release, Nobel Prize in Chemistry 2024, 9 Oct 2024. https://www.nobelprize.org/prizes/chemistry/2024/press-release/
2. Abramson et al., AlphaFold 3, Nature, 8 May 2024. https://www.nature.com/articles/s41586-024-07487-w
3. Addendum to AlphaFold 3 (code release), Nature / PMC, Nov 2024. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11634763/
4. Google DeepMind, AI achieves silver-medal standard at IMO, 25 Jul 2024. https://deepmind.google/discover/blog/ai-solves-imo-problems-at-silver-medal-level
5. Hubert et al., Olympiad-level formal mathematical reasoning with reinforcement learning, Nature, 12 Nov 2025. https://research.google/pubs/olympiad-level-formal-mathematical-reasoning-with-reinforcement-learning/ (DOI 10.1038/s41586-025-09833-y)
6. Google DeepMind, AlphaGeometry, 17 Jan 2024. https://deepmind.google/discover/blog/alphageometry-an-olympiad-level-ai-system-for-geometry/
7. Scientific American, AI reaches silver-medal level, Jul 2024. https://www.scientificamerican.com/article/ai-reaches-silver-medal-level-at-this-years-math-olympiad/
8. Harmonic, Aristotle IMO 2025 announcement, 2025; paper arXiv:2510.01346, 1 Oct 2025. https://harmonic.fun/news/imo-ios ; https://arxiv.org/html/2510.01346v1
9. ByteDance Seed, Seed Prover IMO 2025, Jul 2025. https://seed.bytedance.com/zh/blog/bytedance-seed-prover-achieves-silver-medal-score-in-imo-2025
10. Google DeepMind, FunSearch, 14 Dec 2023; Romera-Paredes et al., Nature (DOI 10.1038/s41586-023-06924-6). https://deepmind.google/blog/funsearch-making-new-discoveries-in-mathematical-sciences-using-large-language-models/
11. FunSearch (summary of results), Wikipedia, accessed 29 Oct 2026. https://en.wikipedia.org/wiki/FunSearch
12. Axios, Google and OpenAI vie for top AI mathlete, 21 Jul 2025. https://www.axios.com/2025/07/21/openai-deepmind-math-olympiad-ai
13. Euronews, Did Google DeepMind or OpenAI win gold, 22 Jul 2025. https://www.euronews.com/next/2025/07/22/did-google-deepmind-or-openai-win-gold-at-the-worlds-most-prestigious-math-competition
14. Google DeepMind, AlphaEvolve, 14 May 2025. https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
15. Novikov et al., AlphaEvolve, arXiv:2506.13131, Jun 2025. https://arxiv.org/abs/2506.13131
16. Popular Science, Human outsmarts DeepMind AI on kissing problem, 2025. https://www.popsci.com/science/human-outsmarts-ai-kissing-problem-math
17. Simple Baselines are Competitive with Code Evolution, arXiv:2602.16805, Feb 2026. https://arxiv.org/pdf/2602.16805
18. The Decoder, OpenAI researcher announced a GPT-5 math breakthrough that never happened, Oct 2025. https://the-decoder.com/leading-openai-researcher-announced-a-gpt-5-math-breakthrough-that-never-happened/
19. Resolution of Erdős Problem #728: a writeup of Aristotle's Lean proof, arXiv:2601.07421, Jan 2026. https://arxiv.org/html/2601.07421v1
20. T. Tao et al., AI contributions to Erdős problems (wiki), data to 30 Jun 2026. https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems
21. Feng et al., Semi-Autonomous Mathematics Discovery with Gemini: a case study on the Erdős problems, arXiv:2601.22401, Jan 2026. https://arxiv.org/html/2601.22401v3
22. The Decoder, AlphaProof Nexus, May 2026 (arXiv:2605.22763, 21 May 2026). https://the-decoder.com/google-deepminds-alphaproof-nexus-solves-decades-old-math-problems-for-a-few-hundred-dollars/
23. OpenAI, An OpenAI model has disproved a central conjecture in discrete geometry, 20 May 2026. https://openai.com/index/model-disproves-discrete-geometry-conjecture/
24. Alon, Bloom, Gowers et al., Remarks on the disproof of the unit distance conjecture, arXiv:2605.20695, May 2026. https://arxiv.org/abs/2605.20695
25. OpenAI, Ten advances in mathematics and theoretical computer science, 1 Aug 2026; Lean certificates. https://openai.com/index/ten-advances-in-mathematics/ ; https://github.com/openai/ten-proofs
26. Quanta Magazine, Why the legendary Erdős problems are falling to AI, 3 Aug 2026. https://www.quantamagazine.org/why-the-legendary-erdos-problems-are-falling-to-ai-20260803/
27. lean-genius issue 43621 (third-party review, low confidence), 2026. https://github.com/rjwalters/lean-genius/issues/43621
28. Equational Theories Project final report, arXiv:2601.20759, Jan 2026; repository. https://arxiv.org/pdf/2601.20759 ; https://reservoir.lean-lang.org/@teorth/equational_theories
29. Lean FRO, Formalizing Fermat's Last Theorem (project page), accessed 29 Oct 2026. https://lean-lang.org/use-cases/flt
30. Anthropic, Formalizing Fermat's Last Theorem, Sep 2026. https://www.anthropic.com/research/formalizing-fermats-last-theorem
31. K. Buzzard, FLT: Anthropic has beaten me to it, Xena Project, 4 Sep 2026. https://xenaproject.wordpress.com/2026/09/04/flt-anthropic-has-beaten-me-to-it/
32. The Next Web, The man paid to prove Fermat by hand says Claude did it in 11 days, Sep 2026. https://thenextweb.com/news/anthropic-claude-fermat-last-theorem-lean-buzzard
33. DeepSeek-Prover-V2, arXiv:2504.21801, 30 Apr 2025. https://arxiv.org/pdf/2504.21801
34. Goedel-Prover-V2, arXiv:2508.03613, Aug 2025. https://arxiv.org/pdf/2508.03613
35. Degrave et al., Magnetic control of tokamak plasmas through deep RL, Nature, 16 Feb 2022. https://pmc.ncbi.nlm.nih.gov/articles/PMC8850200
36. Tracey et al., Towards practical RL for tokamak magnetic control, arXiv:2307.11546, Jul 2023. https://arxiv.org/pdf/2307.11546
37. Seo et al., Avoiding fusion plasma tearing instability with deep RL, Nature, 21 Feb 2024; Princeton news. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10881383/ ; https://mae.princeton.edu/about-mae/news/engineers-use-ai-wrangle-fusion-power-grid
38. Google DeepMind, GraphCast (Science), 14 Nov 2023; arXiv:2212.12794. https://deepmind.google/research/publications/graphcast-learned-global-weather-forecasting/
39. Google DeepMind, GenCast, 4 Dec 2024; MIT Technology Review, 4 Dec 2024. https://deepmind.google/blog/gencast-predicts-weather-and-the-risks-of-extreme-conditions-with-sota-accuracy/ ; https://www.technologyreview.com/2024/12/04/1107892/google-deepminds-new-ai-model-is-the-best-yet-at-weather-forecasting/
40. ECMWF, ECMWF's AI forecasts become operational, 25 Feb 2025; implementation page. https://www.ecmwf.int/node/29308 ; https://confluence.ecmwf.int/display/FCST/Implementation%20of%20AIFS%20Single%20v1
41. Google DeepMind, Weather Lab cyclone predictions, 12 Jun 2025. https://deepmind.google/discover/blog/weather-lab-cyclone-predictions-with-ai/
42. NOAA NHC, 2025 Forecast Verification Report, 2026. https://www.nhc.noaa.gov/verification/pdfs/Verification_2025.pdf
43. Gottweis et al., Towards an AI co-scientist, arXiv:2502.18864, 26 Feb 2025. https://arxiv.org/abs/2502.18864v1
44. Penadés lab et al., AI mirrors experimental science (bioRxiv), 19 Feb 2025. https://www.biorxiv.org/content/10.1101/2025.02.19.639094.full.pdf
45. He, Patkowski et al., Chimeric infective particles expand species boundaries in PICI mobilization, Cell 188, 2025 (DOI 10.1016/j.cell.2025.08.019). https://doi.org/10.1016/j.cell.2025.08.019
46. MIT News, Using AI, MIT researchers identify a new class of antibiotic candidates, 20 Dec 2023. https://news.mit.edu/2023/using-ai-mit-researchers-identify-antibiotic-candidates-1220
47. Nature Medicine, A generative AI-discovered TNIK inhibitor for IPF: randomized phase 2a trial, Nat Med, 3 Jun 2025. https://pubmed.ncbi.nlm.nih.gov/40461817/
48. TechCrunch, Anthropic says its biology lab has already found something big, 23 Sep 2026. https://techcrunch.com/2026/09/23/anthropic-says-its-biology-lab-has-already-found-something-big/
49. Phys.org, Anthropic touts AI-led biology discovery, Sep 2026; Bloomberg, 24 Sep 2026. https://phys.org/news/2026-09-anthropic-touts-ai-biology-discovery.html ; https://www.bloomberg.com/news/articles/2026-09-24/anthropic-biology-discovery-draws-cautious-notes-from-scientists
50. Merchant et al., Scaling deep learning for materials discovery, Nature, 29 Nov 2023. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10700131/
51. Szymanski et al., An autonomous laboratory for the accelerated synthesis of inorganic materials, Nature, 29 Nov 2023. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10700133/
52. Leeman et al., Challenges in high-throughput inorganic materials prediction and autonomous synthesis, PRX Energy 3, 011002, 2024 (preprint Jan 2024). https://chemrxiv.org/engage/chemrxiv/article-details/65957d349138d231611ad8f7
53. Cheetham and Seshadri, Artificial intelligence driving materials discovery?, Chem. Mater., Apr 2024; The Register, 11 Apr 2024. https://pmc.ncbi.nlm.nih.gov/articles/PMC11044265 ; https://www.theregister.com/2024/04/11/google_deepmind_material_study/
54. Karger et al., ForecastBench, arXiv:2409.19839, Sep 2024. https://arxiv.org/pdf/2409.19839
55. Forecasting Research Institute, AI models have likely reached parity with superforecasters on ForecastBench, 2026. https://forecastingresearch.substack.com/p/ai-models-have-likely-reached-parity
56. Good Judgment, What superforecasters actually said about ForecastBench, 2025/2026. https://goodjudgment.com/what-superforecasters-actually-said-about-forecastbench/
