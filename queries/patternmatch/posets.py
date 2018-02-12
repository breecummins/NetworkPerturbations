

def get_poset(dict_of_intervals):
    '''

    :param time_intervals: dictionary of tuples of output lists from sublevel_sets.get_sublevel_sets(),
                            first for mins, second for maxes keyed by unique time series identifier
    :return: list of edges
    '''
    # check if max/min of same identifier overlap
    pass