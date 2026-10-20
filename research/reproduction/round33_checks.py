"""Round-33 checks for the Codex finding on PR #4 at 2d0fbeb (no reference code, no network).

Codex's review 5563281370 of 2d0fbeb, one inline finding, 4307298084 (RC-215): version 29 puts a member listed in a
later window than its cluster's batch b(k) outside every confirmatory statistic, while the section 6 estimand is
stated over the eligible-event population of each cluster taken over all members. When a source lists a follow-up
member after the first member's outcome, the first-window mean and the all-member cluster mean differ, so the
version-29 statistic does not control the null the estimand row states.

Setting of Appendix AF: 600 clusters, cluster increment +-0.2 on the first-window member, one-sided t at the nominal
1.645, 20,000 replications.
"""
import json
import numpy as np

out = {}
REPS, N, CRIT = 20_000, 600, 1.645


def t_reject(s, keep=None):
    n = s.shape[1]
    m = s.mean(1)
    sd = s.std(1, ddof=1)
    rej = m / (sd / np.sqrt(n)) > CRIT
    if keep is not None:
        rej &= keep
    return round(float(rej.mean()), 4)


# ================= 4307298084 (RC-215): outcome-triggered follow-up members =================
# Law F(delta, q): the first-window member's increment x1 is +0.2 with probability 0.5 + delta/0.4 and -0.2 otherwise
# (E x1 = delta). After x1 = -0.2 the source lists a follow-up member in a later window with probability q, and the
# follow-up's increment is x2 = -0.6. A cluster's all-member score is x1 without a follow-up and (x1 + x2)/2 = -0.4
# with one, so E[all-member score] = delta - 0.2 q (0.5 - 2.5 delta), which is zero at delta = 0.1 q / (1 + 0.5 q).
# Statistics: first_window, the t test on x1 (the version-29 primary; a follow-up is a post-registration member);
# all_member, the t test on the all-member score with every follow-up observed (Codex's route of keeping cross-window
# members, at a fixed horizon with no censoring at T_D); withhold_if_any_follow_up, the first-window test with the
# claim made non-confirmatory whenever any cluster of the cohort has a follow-up (Codex's other route).
rng = np.random.default_rng(3301)


def simulate(delta, q):
    x1 = np.where(rng.random((REPS, N)) < 0.5 + delta / 0.4, 0.2, -0.2)
    follow = (x1 < 0) & (rng.random((REPS, N)) < q)
    s_all = np.where(follow, (x1 - 0.6) / 2, x1)
    return {'mean_first_window': round(float(x1.mean()), 5), 'mean_all_member': round(float(s_all.mean()), 5),
            'first_window': t_reject(x1), 'all_member': t_reject(s_all),
            'withhold_if_any_follow_up': t_reject(x1, keep=~follow.any(1))}


all_member_null, registration_time_null = {}, {}
for q in (0.05, 0.10, 0.20):
    delta = 0.1 * q / (1 + 0.5 * q)
    all_member_null[f'q={q}'] = {'delta': round(delta, 6), **simulate(delta, q)}
    registration_time_null[f'q={q}'] = {'delta': 0.0, **simulate(0.0, q)}
out['4307298084 RC-215 all-member null (estimand of 17 v29 section 6 as written)'] = all_member_null
out['4307298084 RC-215 registration-time null (estimand of 17 v30 section 6)'] = registration_time_null

# Remedy: the section 6 estimand is stated over each eligible cluster's registration-time members, those listed in
# window b(k). Every such member is listed before the end of window b(k) < t_reg,b(k) < its not_before, so the
# membership is fixed before any member's outcome is knowable (a definition, not checked here), and the version-29
# statistic tests exactly this null: first_window rejects at the nominal rate under the registration-time null.
# Post-registration members stay in the exhaustive candidate log and are reported as an exploratory secondary.

print(json.dumps(out, indent=1))
