import numpy as np

def normalize(curve):
    '''
    :param curve: a dictionary representing a function, times key values
    :return: a dictionary representing a normalized function in [-0.5,0.5], times key values
    '''
    times = [t for t in curve]
    vals = np.array([curve[t] for t in times])
    nvals = (vals - float(np.min(vals))) / (np.max(vals) - np.min(vals)) - 0.5
    return dict((t, n) for (t, n) in zip(times, nvals))

def invert(curve):
    '''
    Use only on output of normalize.
    :param curve: a dictionary representing a function, times key values
    :return:
    '''
    return dict( (t,-1*n) for (t,n) in curve.iteritems())

def get_derivative(curve):
    pass