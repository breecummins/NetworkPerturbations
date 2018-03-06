import pytest


def get_sublevel_sets(births_only_merge_tree,curve,eps):
    '''
    Calculates the sublevel set interval for every minimum in curve that exceeds a threshold.
    :param births_only_merge_tree: merge tree dict with intermediate points removed
    :param curve: dict with times keying function values (Curve.curve or Curve.normalized)
    :param eps: float threshold (noise level) For normalized curves, 0 < eps < 1.
    :return: dict of minima birth times keying lifetime intervals
    '''
    too_small = [u for u,(s,v) in births_only_merge_tree.iteritems() if u!=v and abs(curve[u] - curve[s]) < eps]
    for u in too_small:
        births_only_merge_tree.pop(u)
    times = sorted([k for k in curve])
    time_intervals = dict()
    for b in births_only_merge_tree:
        i = times.index(b)
        j = i
        while j < len(times)-1 and abs(curve[times[j]] - curve[times[i]]) <= 2*eps:
            j += 1
        upper = j if abs(curve[times[j]] - curve[times[i]]) <= 2*eps else j-1
        j = i
        while j > 0 and abs(curve[times[j]] - curve[times[i]]) <= 2*eps:
            j -= 1
        lower = j if abs(curve[times[j]] - curve[times[i]]) <= 2*eps else j+1
        time_intervals[b] = (times[lower],times[upper])
    return time_intervals


def minimal_time_ints(births_only_merge_tree,curve,eps):
    '''
    Produce merge tree and remove intervals that overlap by picking deeper min
    (shorter interval). The remaining intervals are the "epsilon minimum intervals."
    :param births_only_merge_tree: merge tree dict with intermediate points removed
    :param curve: dict with times keying function values (Curve.curve or Curve.normalized)
    :param eps: float threshold (noise level) For normalized curves, 0 < eps < 1.
    :return: dict of minima birth times each keying the associated (closed) epsilon-minimum interval
    '''
    ti = get_sublevel_sets(births_only_merge_tree,curve,eps)
    stack = [v for v in ti]
    for u in stack:
        if any([u != v and ti[u][0] <= ti[v][0] and ti[u][1] >= ti[v][1] for v in ti]):
            ti.pop(u)
    return ti


def test():
    import triplet_merge_trees as tmt
    from curve import Curve

    curve = Curve({0:-2, 1:2, 2:0, 3:3, 4:-4, 5:1, 6:-7})
    births_only_merge_tree = tmt.births_only(curve.curve)
    time_ints = minimal_time_ints(dict(births_only_merge_tree), curve.curve, 0.75)
    assert(time_ints=={0: (0, 0), 2: (2, 2), 4: (4, 4), 6: (6, 6)})
    time_ints = minimal_time_ints(dict(births_only_merge_tree), curve.curve, 2)
    assert(time_ints=={0: (0, 2), 4: (4, 4), 6: (6, 6)})
    time_ints = minimal_time_ints(dict(births_only_merge_tree), curve.curve, 3)
    assert(time_ints=={6: (6, 6)})
    curve2 = Curve({0:0, 1:-1, 2:-2, 3:1, 4:3, 5:6, 6:2})
    births_only_merge_tree = tmt.births_only(curve2.curve)
    time_ints = minimal_time_ints(dict(births_only_merge_tree), curve.curve, 0.75)
    assert(time_ints == {2: (2, 2), 6: (6, 6)})
    time_ints = minimal_time_ints(dict(births_only_merge_tree), curve.curve, 1)
    assert(time_ints == {2: (0, 2), 6: (6, 6)})
    time_ints = minimal_time_ints(dict(births_only_merge_tree), curve.curve, 3)
    assert(time_ints == {2: (0, 5), 6: (6, 6)})
