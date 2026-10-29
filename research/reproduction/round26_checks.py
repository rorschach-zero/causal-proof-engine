"""Round-26 checks for the Codex findings on PR #4 at 89286f9 (no reference code, no network).

Codex's automatic review of 89286f9, posted as PR #4 comment 6249483566 (four findings, keyed by order):
6249483566/1 (RC-189, a commit identity; checked with git, no block here), 6249483566/2 (RC-190, the header of 16;
textual), 6249483566/3 (RC-191, a candidate log that records only the candidates the registrar considered),
6249483566/4 (RC-192, the label PROVED; textual).

Setting of RC-187 (Appendix Y): 200 eligible clusters, half with mean increment +d and half -d, so the
eligible-population mean is exactly zero; noise sd sigma; Bernoulli inclusion at pi = 0.5 drawn from
SHA-256(s_b || id) with s_b unknown to the registrar; one-sided test of the included mean at the nominal 1.645 and at
the illustrated c* = 2.254.
"""
import hashlib
import json
import math
import numpy as np

out = {}

# ================= 6249483566/3 (RC-191): a candidate log of the candidates "considered" =================
# The draws are unchosen (RC-187), but the registrar decides which predicate-matching candidates reach the log. A
# registrar who does not log a fraction f of the negative stratum gives those clusters inclusion probability zero.
# Remedy: the batch is the complete predicate-matching listing of the source, audited against the source's own
# archive; an omitted candidate gets its draw from the same s_b, and a drawn omission enters as a missing cluster
# (VOID cap, box rule). The honest sample (every eligible candidate, drawn by the rule) is then recoverable.
rng = np.random.default_rng(2191)
NC, D, SIG, PI, H = 200, 0.01, 0.02, 0.5, 20000
mu = np.where(np.arange(NC) < NC // 2, D, -D)
neg = np.arange(NC) >= NC // 2

def t_stat(x):
    return x.mean() / (x.std(ddof=1) / math.sqrt(x.size))

def omission(f):
    rej_nom = rej_cal = rej_honest_nom = rej_honest_cal = 0
    shift = 0.0
    drawn_omitted = included = 0
    n_omit = int(round(f * NC // 2))
    for _ in range(H):
        draws = rng.random(NC) < PI
        x_all = mu + SIG * rng.standard_normal(NC)
        omitted = np.zeros(NC, dtype=bool)
        if n_omit:
            omitted[rng.choice(np.flatnonzero(neg), n_omit, replace=False)] = True
        keep = draws & ~omitted
        t = t_stat(x_all[keep])
        rej_nom += t > 1.645
        rej_cal += t > 2.254
        shift += mu[keep].mean()
        th = t_stat(x_all[draws])
        rej_honest_nom += th > 1.645
        rej_honest_cal += th > 2.254
        drawn_omitted += int((draws & omitted).sum())
        included += int(draws.sum())
    return {'logged_only': {'rejection_at_1.645': round(rej_nom / H, 4), 'rejection_at_2.254': round(rej_cal / H, 4),
                            'mean_included_true_effect': round(shift / H, 5)},
            'honest_sample_after_audit': {'rejection_at_1.645': round(rej_honest_nom / H, 4),
                                          'rejection_at_2.254': round(rej_honest_cal / H, 4)},
            'drawn_omissions_share_of_honest_sample': round(drawn_omitted / included, 4)}

rc191 = {'clusters': NC, 'd': D, 'sigma': SIG, 'pi': PI, 'histories': H}
for f in (0.0, 0.1, 0.25, 0.5):
    rc191[f'omitted_share_of_negative_stratum={f}'] = omission(f)

# The draw of an omitted candidate is re-derivable from the anchored batch and the beacon value, whether or not the
# candidate is in the batch, and the batch content cannot steer it because v_b is published after the anchor.
def draw(s_b, cid, pi):
    return int.from_bytes(hashlib.sha256(s_b + cid.encode()).digest(), 'big') < int(pi * 2 ** 256)

listing = [f'src-A/{i:04d}' for i in range(40)]
logged = [c for i, c in enumerate(listing) if i % 4 != 3]       # every fourth candidate never reaches the log
batch = json.dumps(logged, separators=(',', ':')).encode()
v_b = hashlib.sha256(b'fixture beacon round published after the anchor of batch b').digest()
s_b = hashlib.sha256(batch + v_b).digest()
omitted_ids = sorted(set(listing) - set(logged))
rc191['audit_fixture'] = {
    'listing': len(listing), 'logged': len(logged), 'omissions_found_by_audit': len(omitted_ids),
    'omissions_drawn': sum(draw(s_b, c, PI) for c in omitted_ids),
    'logged_drawn': sum(draw(s_b, c, PI) for c in logged),
}
out['6249483566/3 RC-191'] = rc191

print(json.dumps(out, indent=1))
