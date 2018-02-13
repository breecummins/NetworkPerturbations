import triplet_merge_trees as tmt
import sublevel_sets as ss


def get_mins_maxes(name,curve,eps):
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
    labeled_mins = [zip(time_ints_mins,[name + " min"]*len(time_ints_mins))]
    labeled_maxs = [zip(time_ints_maxs,[name + " max"]*len(time_ints_maxs))]
    return sorted(labeled_mins+labeled_maxs)


def get_poset(dict_of_intervals):
    '''

    :param time_intervals: dictionary of tuples of output lists from sublevel_sets.get_sublevel_sets(),
                            first for mins, second for maxes keyed by unique time series identifier
    :return: list of edges
    '''
    # check if max/min of same identifier overlap
    pass