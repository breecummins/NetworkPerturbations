import triplet_merge_trees as tmt
import sublevel_sets as ss


def get_mins_maxes(name,curve,eps):
    '''
    For a given (named) curve and threshold eps, find the eps-minimum intervals of
    both the maxima and minima of the curve.
    :param name: A string uniquely identifying the time series (curve).
    :param curve: dict with times keying function values
    :param eps: float threshold (noise level) with 0 < eps < 1.
    :return: sorted list of tuples where first element is sublevel set interval and
             second element is name + extrema type
    '''
    n = curve.normalized
    i = curve.normalized_inverted
    merge_tree_mins = tmt.births_only(n)
    merge_tree_maxs = tmt.births_only(i)
    time_ints_mins = ss.minimal_time_ints(merge_tree_mins,n,eps)
    time_ints_maxs = ss.minimal_time_ints(merge_tree_maxs,i,eps)
    for m,(tm0,tm1) in time_ints_mins.iteritems():
        for M,(tM0,tM1) in time_ints_maxs.iteritems():
            if (m < M and tm1 > tM0) or (M < m and tM1 > tm0):
                # eps is too big and we have min/max overlap
                return None
    labeled_mins = [(v,(name,"min")) for t,v in time_ints_mins.iteritems()]
    labeled_maxs = [(v,(name,"max")) for t,v in time_ints_maxs.iteritems()]
    both = sorted(labeled_mins+labeled_maxs)
    #FIXME: check for alternating max/min (I think this should always be true)
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
            if ae:
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
    from curve import Curve
    curve1 = Curve({0:-2, 1:2, 2:0, 3:3, 4:-4, 5:1, 6:-7})
    curve2 = Curve({0:0, 1:-1, 2:-2, 3:1, 4:3, 5:6, 6:2})

    curves = {"X":curve1, "Y":curve2}
    epsilons = [0.01,0.05,0.1,0.2]

    posets = main(curves, epsilons)
    for p in posets:
        print(p)
        print("\n\n")

    print("Poset 0.01 == poset 0.05: {}".format(posets[0]==posets[1]))
    print("Poset 0.01 == poset 0.10: {}".format(posets[0]==posets[2]))

    # import matplotlib.pyplot as plt
    # times = range(7)
    # vals1 = [curve1.normalized[t] for t in times]
    # vals2 = [curve2.normalized[t] for t in times]
    # plt.plot(times,vals1,label="X")
    # plt.plot(times,vals2,label="Y")
    # plt.legend()
    # plt.show()

if __name__ == "__main__":
    test()