def get_sublevel_sets(births_only_merge_tree,curve,eps):
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
    # Produce merge tree and remove intervals that overlap by
    # picking deeper min (shorter interval)
    # the remaining intervals are the "epsilon minimum intervals"
    ti = get_sublevel_sets(births_only_merge_tree,curve,eps)
    stack = [v for v in ti]
    for u in stack:
        if any([u != v and ti[u][0] <= ti[v][0] and ti[u][1] >= ti[v][1] for v in ti]):
            ti.pop(u)
    return ti


def test():
    import triplet_merge_trees as tmt
    curve = {0:-2, 1:2, 2:0, 3:3, 4:-4, 5:1, 6:-7}
    births_only_merge_tree = tmt.births_only(curve)
    time_ints = get_sublevel_sets(births_only_merge_tree, curve, 0.75)
    time_ints = minimal_time_ints(time_ints)
    print(time_ints=={0: (0, 0), 2: (2, 2), 4: (4, 4), 6: (6, 6)})
    time_ints = get_sublevel_sets(births_only_merge_tree, curve, 2)
    time_ints = minimal_time_ints(time_ints)
    print(time_ints=={0: (0, 2), 4: (4, 4), 6: (6, 6)})
    time_ints = get_sublevel_sets(births_only_merge_tree, curve, 3)
    time_ints = minimal_time_ints(time_ints)
    print(time_ints=={6: (6, 6)})

    # import matplotlib.pyplot as plt
    # import numpy as np
    #
    # times = sorted([t for t in curve])
    # vals = np.array([curve[t] for t in times])
    # plt.plot(times,vals,color='r')
    # plt.show()

if __name__ == "__main__":
    test()
