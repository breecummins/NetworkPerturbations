import numpy as np
import itertools
import pytest


class Curve(object):

    def __init__(self,curve,perturb=1.e-10):
        '''
        Collection of methods on dictionary representation of function.
        :param curve: a dictionary representing a function, times keying values
        :param perturb: small perturbation float
       '''
        self.original_curve = curve
        self.curve = self.make_unique(dict(curve),perturb)
        self.normalized = self.normalize()
        self.normalized_inverted = self.invert(self.normalized)

    def make_unique(self,curve,perturb):
        '''
        Alter identical values slightly.
        :param curve: a dictionary representing a function, times key values
        :param perturb: small perturbation float
        :return:
        '''
        identical = None
        for (c,v),(d,w) in itertools.product(curve.iteritems(),curve.iteritems()):
            if c != d and v == w:
                identical = c
                break
        if identical is not None:
            curve[identical] += perturb
            return self.make_unique(curve,perturb)
        return curve

    def normalize(self):
        '''
        Normalize function in [-0.5,0.5].
        :return: a dictionary representing a normalized function, times key values
        '''
        times = [t for t in self.curve]
        vals = np.array([self.curve[t] for t in times])
        nvals = (vals - float(np.min(vals))) / (np.max(vals) - np.min(vals)) - 0.5
        return dict((t, n) for (t, n) in zip(times, nvals))

    def invert(self,curve=None):
        '''
        Sign-invert function values.
        For epsilon perturbations call self.invert(self.normalize()).
        :return: a dictionary representing a function, times key sign-reversed values
        '''
        if curve is None:
            curve=self.curve
        return dict((t,-1*n) for (t,n) in curve.iteritems())

    def get_derivative(self):
        #FIXME
        self.derivative = dict()


def test():
    curve = Curve({0:-2, 1:2, 2:0, 3:1, 4:-2, 5:1, 6:-7})
    new_curve = Curve(curve.curve)
    assert(new_curve.original_curve == new_curve.curve)
    assert(curve.curve == Curve(curve.invert()).invert())
