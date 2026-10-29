"""Finite-state probability-coherence engine.

The engine detects incompatible probabilistic judgments and logical implication
claims. It does NOT establish that the logical links are empirically true.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from math import isclose
from typing import Mapping
from scipy.optimize import linprog


@dataclass(frozen=True)
class ProbabilityInterval:
    lower: float
    upper: float

    def validate(self):
        if not 0 <= self.lower <= self.upper <= 1:
            raise ValueError('Probability interval must be within [0,1]')


@dataclass(frozen=True)
class CoherentWorlds:
    events: tuple[str, ...]
    worlds: tuple[tuple[bool, ...], ...]
    probabilities: tuple[float, ...]
    def marginal(self, event: str) -> float:
        i = self.events.index(event)
        return sum(q for w, q in zip(self.worlds, self.probabilities) if w[i])
    def verify(self, intervals: Mapping[str,ProbabilityInterval], tol=1e-7) -> bool:
        return (abs(sum(self.probabilities)-1) < tol and
                all(p >= -tol for p in self.probabilities) and
                all(interval.lower-tol <= self.marginal(name) <= interval.upper+tol
                    for name, interval in intervals.items()))


def coherent_joint(
    event_intervals: Mapping[str, ProbabilityInterval],
    implications: tuple[tuple[str,str], ...] = (),
) -> CoherentWorlds | None:
    """Find any coherent joint distribution with user-declared A => B restrictions.

    Feasibility by LP. The implication assumptions MUST carry external evidence
    in production; no assumption is inferred from prose automatically.
    """
    events = tuple(sorted(event_intervals))
    if not events or len(events)>14:
        raise ValueError('1-14 events allowed in prototype (2^n enumeration)')
    for x in event_intervals.values():
        x.validate()
    for a,b in implications:
        if a not in events or b not in events:
            raise ValueError('Unrecognized event')
    index={name:i for i,name in enumerate(events)}
    worlds=tuple(w for w in product((False,True),repeat=len(events))
                 if all((not w[index[a]]) or w[index[b]] for a,b in implications))
    if not worlds:
        return None
    indicator=[[1.0 if w[i] else 0.0 for w in worlds] for i in range(len(events))]
    A_ub=[]; b_ub=[]
    for i,name in enumerate(events):
        A_ub.extend((indicator[i], [-x for x in indicator[i]]))
        b_ub.extend((event_intervals[name].upper,-event_intervals[name].lower))
    sol=linprog(c=[0.0]*len(worlds),A_eq=[[1.0]*len(worlds)],b_eq=[1.0],
                A_ub=A_ub,b_ub=b_ub,bounds=(0.0,None),method='highs')
    if not sol.success:
        return None
    out=CoherentWorlds(events,worlds,tuple(float(x) for x in sol.x))
    if not out.verify(event_intervals):
        raise ArithmeticError('LP returned non-coherent distribution')
    return out


def event_probability_bounds(event_intervals: Mapping[str,ProbabilityInterval],
                             target_event: str, implications: tuple[tuple[str,str],...]=()) -> tuple[float,float] | None:
    events=tuple(sorted(event_intervals))
    if not events or len(events)>14:
        raise ValueError('1-14 events allowed in prototype (2^n enumeration)')  # v0.2: guard was missing
    if target_event not in events:
        raise ValueError('Target not among events')
    for interval in event_intervals.values():
        interval.validate()
    index={e:i for i,e in enumerate(events)}
    worlds=tuple(w for w in product((False,True),repeat=len(events))
                 if all((not w[index[a]]) or w[index[b]] for a,b in implications))
    if not worlds:
        return None
    A_ub=[]; b_ub=[]
    for i,name in enumerate(events):
        inds=[1.0 if w[i] else 0.0 for w in worlds]
        A_ub += [inds,[-x for x in inds]]
        b_ub += [event_intervals[name].upper,-event_intervals[name].lower]
    target=[1.0 if w[index[target_event]] else 0.0 for w in worlds]
    kw=dict(A_eq=[[1.0]*len(worlds)],b_eq=[1.0],A_ub=A_ub,b_ub=b_ub,
            bounds=(0,None),method='highs')
    minres=linprog(c=target,**kw)
    maxres=linprog(c=[-x for x in target],**kw)
    if not (minres.success and maxres.success):
        return None
    return (max(0,float(minres.fun)),min(1,float(-maxres.fun)))
