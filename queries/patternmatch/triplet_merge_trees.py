import pytest


def compute_merge_tree(curve):
    '''
    This code assumes that all function values in the series are distinct.
    This is automatically done in the class Curve.
    :param curve: dict with float times keying function float values (Curve.curve or Curve.normalized)
    :return: triplet merge tree representation --
             a dict with a time keying a tuple of times, T[u] = (s,v),
             where u obtains label v at time s (branch decomposition)

    reference: Dmitriy Smirnov and Dmitriy Morozov Chapter 1 Triplet Merge Trees
    people.csail.mit.edu/smirnov/publications/tmt.pdf
    Algorithms 1 & 2
    '''

    def finddeepest(u):
        u1 = deepest[u]
        (_,v) = T[u1]
        while u1 != v:
            u1 = deepest[v]
            (_,v) = T[u1]
        d = u1
        u1 = deepest[u]
        (_, v) = T[u1]
        while u1 != v:
            u1 = deepest[v]
            deepest[v] = d
            (_, v) = T[u1]
        deepest[u] = d
        return d

    T = dict( (t,(t,t)) for t in curve )
    deepest = dict( (t,t) for t in curve )
    times = sorted([t for t in curve])
    edges = zip(times[:-1],times[1:])
    sorted_verts = [a for (a,b) in sorted(curve.iteritems(), key=lambda t : t[1])]
    for u in sorted_verts:
        leaves = []
        for e in edges:
            if u in e:
                v = e[0] if u != e[0] else e[1]
                if curve[v] < curve[u]:
                    leaves.append(finddeepest(v))
        if len(leaves) > 0:
            inds = sorted(zip([sorted_verts.index(l) for l in leaves],leaves))
            w = min(inds)[1]
            T[u] = (u,w)
            leaves.remove(w)
            for x in leaves:
                T[x] = (u,w)
    return T


def births_only(curve):
    '''
    Computes merge tree and then removes all intermediate points and keeps only minima.
    :param curve: dict with times keying function values (Curve.curve or Curve.normalized)
    :return: triplet merge tree representation --
             a dict with a time keying a tuple of times, T[u] = (s,v),
             where u obtains label v at time s (branch decomposition)
    '''
    merge_tree = compute_merge_tree(curve)
    no_births = [u for u, (s, v) in merge_tree.iteritems() if u == s and u!=v]
    for u in no_births:
        merge_tree.pop(u)
    return merge_tree


def test():
    from curve import Curve
    curve = Curve({0:-2, 1:2, 2:0, 3:3, 4:-4, 5:1, 6:-7})
    tmt = {0:(3,6),1:(1,0),2:(1,0),3:(3,6),4:(5,6),5:(5,6),6:(6,6)}
    assert(tmt == compute_merge_tree(curve.curve))
    assert(tmt == compute_merge_tree(curve.normalized))
    tMt = {0:(0,3),1:(2,3),2:(2,3),3:(3,3),4:(4,3),5:(4,3),6:(6,3)}
    assert(tMt == compute_merge_tree(curve.normalized_reflected))
    curve2 = Curve({0:0, 1:-1, 2:-2, 3:1, 4:3, 5:6, 6:2})
    tmt2 = {0:(0,2),1:(1,2),2:(2,2),3:(3,2),4:(4,2),5:(5,2),6:(5,2)}
    assert(tmt2 == compute_merge_tree(curve2.curve))
    assert(tmt2 == compute_merge_tree(curve2.normalized))
    tMt2 = {0:(2,5),1:(1,0),2:(2,5),3:(3,5),4:(4,5),5:(5,5),6:(6,5)}
    assert(tMt2 == compute_merge_tree(curve2.normalized_reflected))

    import numpy as np
    x = np.arange(-2.5, 5.01, 0.01)
    y = -0.25 * x ** 4 + 4.0/3 * x ** 3 + 0.5 * x ** 2 - 4.0 * x
    curve = Curve({t: v for (t, v) in zip(x, y)})
    B=births_only(curve.curve)
    C = {}
    # there is round-off error in the computations
    # round to 10th decimal place for comparison
    for b in B.iteritems():
        C[round(b[0],10)] = (round(b[1][0],10),round(b[1][1],10))
    tmt = {-2.5: (-2.5, -2.5), 5.0: (4.0, -2.5), 1.0: (-1.0, -2.5)}
    assert(C == tmt)








