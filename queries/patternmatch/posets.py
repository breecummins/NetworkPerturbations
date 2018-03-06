import triplet_merge_trees as tmt
import sublevel_sets as ss
import pytest


def get_mins_maxes(name,curve,eps):
    '''
    For a given (named) curve and threshold eps, find the eps-minimum intervals of
    both the maxima and minima of the curve.
    :param name: A string uniquely identifying the time series (curve).
    :param curve: dict with float times keying float function values
    :param eps: float threshold (noise level) with 0 < eps < 1.
    :return: sorted list of tuples where first element is sublevel set interval and
             second element is name + extrema type
    '''
    n = curve.normalized
    i = curve.normalized_reflected
    merge_tree_mins = tmt.births_only(n)
    merge_tree_maxs = tmt.births_only(i)
    time_ints_mins = ss.minimal_time_ints(merge_tree_mins,n,eps)
    time_ints_maxs = ss.minimal_time_ints(merge_tree_maxs,i,eps)
    labeled_mins = [(v,(name,"min")) for _,v in time_ints_mins.iteritems()]
    labeled_maxs = [(v,(name,"max")) for _,v in time_ints_maxs.iteritems()]
    both = sorted(labeled_mins+labeled_maxs)
    both = prune_overlap(both[:])
    extrema = [b[1][-3:] for b in both]
    if any(x==y for (x,y) in zip(extrema[:-1],extrema[1:])):
        # This shouldn't ever happen
        raise ValueError("Two minima or two maxima in a row.")
    return both

def prune_overlap(both):
    # get rid of overlapping mins and maxs

    def combine(sublist):
        m = sorted([o[0][0] for o in sublist])[0]
        M = sorted([o[0][1] for o in sublist])[-1]
        both.append(((m, M), sublist[0][1]))

    z = zip(both[:-1],both[1:])
    overlap = set([])
    while len(z) > 0:
        (a,b) = z.pop(0)
        while a[0][1] > b[0][0]:
            overlap.add(a)
            overlap.add(b)
            (a,b) = z.pop(0)
        if len(overlap)%2 == 1:
            mins = [o for o in overlap if o[1][1]=="min"]
            if len(mins) > len(overlap)/2.0:
                combine(mins)
            else:
                maxs = [o for o in overlap if o[1][1]=="max"]
                combine(maxs)
        for o in overlap:
            both.remove(o)
        overlap = set([])
        both.sort()
    return both

def get_poset(all_extrema):
    ints,names = zip(*all_extrema)
    edges = []
    for j,a in enumerate(ints):
        for k,b in enumerate(ints):
            # could <= here instead, it's a choice
            if a[1] < b[0]:
                edges.append((j,k))
    return names,edges


def main(curves,epsilons):
    '''

    :param curves: dict of instances of Curve, each keyed by unique name
    :param epsilons: list of threshold epsilons
    :return:
    '''
    flag="go"
    posets = []
    for eps in sorted(epsilons):
        all_extrema = []
        for name,curve in curves.iteritems():
            ae = get_mins_maxes(name,curve,eps)
            if len(ae) > 1:
                all_extrema.extend(ae)
            else:
                print("Warning: Epsilon = {:.3f} is too large to distinguish extrema. No poset returned.".format(eps))
                flag = "stop"
                break
        if flag == "stop":
            break
        else:
            posets.append(get_poset(all_extrema))
    return posets


def test():
    '''
    Note: Assertions may fail due to noise level. Check if zero noise level is returning correctly.
    If so, reduce the random noise levels and see if that fixes the problem.
    '''
    from curve import Curve
    import numpy as np

    x = np.arange(-2.5,5.01,0.01)
    y = -0.25*x**4 + 4.0/3*x**3 + 0.5*x**2 - 4.0*x
    z = 0.6 * (0.25 * x ** 4 - 1.6 / 3 * x ** 3 - 4.35 / 2 * x ** 2 + 0.45 * x)
    noises = [0.0, 0.001, 0.002] #have to have very small noise for posets to stay the same.

    def check_output_singles(u,pos,noise_std,eps):
        np.random.seed(0)
        noise = np.random.normal(0,noise_std,u.shape)
        curve = Curve({ t : v for (t,v) in zip(x,u+noise) })
        assert(pos == get_poset(get_mins_maxes("curve",curve,eps)))

    def check_output_doubles(pos,n,eps):
        np.random.seed(0)
        noise = np.random.normal(0,n,y.shape)
        curvey = Curve({ t : v for (t,v) in zip(x,y+noise) })
        curvez = Curve({ t : v for (t,v) in zip(x,z+noise) })
        assert(pos == main({"y":curvey,"z":curvez},[eps])[0])

    epsilons = [0.01,0.05]
    posy1 = ((('curve', 'min'), ('curve', 'max'), ('curve', 'min'), ('curve', 'max'), ('curve', 'min')),
           [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)])
    posz1 = ((('curve', 'max'), ('curve', 'min'), ('curve', 'max'), ('curve', 'min'), ('curve', 'max')),
           [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)])
    posb1 = ((('y', 'min'), ('y', 'max'), ('y', 'min'), ('y', 'max'), ('y', 'min'), ('z', 'max'), ('z', 'min'), ('z', 'max'), ('z', 'min'), ('z', 'max')), [(0, 1), (0, 2), (0, 3), (0, 4), (0, 6), (0, 7), (0, 8), (0, 9), (1, 2), (1, 3), (1, 4), (1, 8), (1, 9), (2, 3), (2, 4), (2, 8), (2, 9), (3, 4), (3, 9), (5, 1), (5, 2), (5, 3), (5, 4), (5, 6), (5, 7), (5, 8), (5, 9), (6, 2), (6, 3), (6, 4), (6, 7), (6, 8), (6, 9), (7, 3), (7, 4), (7, 8), (7, 9), (8, 3), (8, 4), (8, 9)])
    posy5 = ((('curve', 'min'), ('curve', 'max'), ('curve', 'min')), [(0, 1), (0, 2), (1, 2)])
    posz5 = ((('curve', 'min'), ('curve', 'max')), [(0, 1)])
    posb5 = ((('y', 'min'), ('y', 'max'), ('y', 'min'), ('z', 'min'), ('z', 'max')), [(0, 1), (0, 2), (0, 4), (1, 2), (1, 4), (3, 2), (3, 4)])
    posets = ((posy1,posz1,posb1),(posy5,posz5,posb5))
    for (eps,pos) in zip(epsilons,posets):
        for n in noises:
            if eps == 0.01:
                check_output_singles(y,pos[0],n,eps)
                check_output_singles(z,pos[1],n,eps)
                check_output_doubles(pos[2], n, eps)
    pos=((('y', 'min'), ('y', 'max'), ('y', 'min'), ('y', 'max'), ('y', 'min'), ('z', 'max'), ('z', 'min'), ('z', 'max'), ('z', 'min'), ('z', 'max')), [(0, 1), (0, 2), (0, 3), (0, 4), (0, 6), (0, 7), (0, 8), (0, 9), (1, 2), (1, 3), (1, 4), (1, 7), (1, 8), (1, 9), (2, 3), (2, 4), (2, 8), (2, 9), (3, 4), (3, 9), (5, 1), (5, 2), (5, 3), (5, 4), (5, 6), (5, 7), (5, 8), (5, 9), (6, 1), (6, 2), (6, 3), (6, 4), (6, 7), (6, 8), (6, 9), (7, 2), (7, 3), (7, 4), (7, 8), (7, 9), (8, 3), (8, 4), (8, 9)])
    check_output_doubles(pos, 0, 0.0025)

