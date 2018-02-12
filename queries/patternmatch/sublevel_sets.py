

def get_births(merge_tree,eps):
    return [trip[0] for trip in merge_tree if trip[0] == trip[2] or trip[1]-trip[0] > eps]


def get_sublevel_sets(merge_tree,curve,eps):
    times = sorted([k for k in curve])
    births = get_births(merge_tree,eps)
    time_intervals = []
    for b in births:
        i = times.index(b)
        j=i+1
        while j < len(times) and abs(curve[times[j]] - curve[times[i]]) < 2*eps:
            j += 1
        upper = j if abs(curve[times[j]] - curve[times[i]]) == 2*eps else j-1
        j = i-1
        while j >= 0 and abs(curve[times[j]] - curve[times[i]]) < 2*eps:
            j -= 1
        lower = j if abs(curve[times[j]] - curve[times[i]]) == 2*eps else j+1
        time_intervals.append((times[lower],times[upper]))
    return time_intervals
