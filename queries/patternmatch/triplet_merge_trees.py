# reference: Dmitriy Smirnov and Dmitriy Morozov Chapter 1 Triplet Merge Trees
# people.csail.mit.edu/smirnov/publications/tmt.pdf


import operator

#FIXME: Double-check that this actually works for maxima

def ComputeMergeTree(curve, type="min"):
    '''
    :param curve: dict with times keying function values
    :param type: "min" or "max"
    :return: triplet merge tree representation, a dict with a time keying a tuple of times, T[u] = (s,v)

    '''

    if type == "min":
        op = operator.lt
        ope = operator.le
    else:
        op = operator.gt
        ope = opertor.ge

    def Merge(T, u, s, v):
        (u1, su, u2) = Representative(T, u, s)
        (v1, sv, v2) = Representative(T, v, s)
        if u1 == v1: # u1 == v2? possible typo?
            return T
        if op(curve[v1], curve[u1]):
            (u1, su, u2), (v1, sv, v2) = (v1, sv, v2), (u1, su, u2)
        T[v1] = (s, u1)
        return Merge(T, u1, sv, v2)

    def Representative(T, u, s):
        a = curve[s]
        (s,v) = T[u]
        while s != v and ope(curve[s], a):
            u = v
            (s,v) = T[u]
        return (u,s,v)

    T = dict( (t,(t,t)) for t in curve )
    times = sorted([t for t in curve])
    for k in range(len(times[:-1])):
        u,v = times[k],times[k+1]
        if op(curve[u],curve[v]):
            T = Merge(T,v,v,u)
        else:
            T = Merge(T,u,u,v)
    for u in T:
        # Repair algorithm from paper
        (s,_) = T[u]
        (_,_,v) = Representative(T,u,s)
        if u != v: T[u] = (s,v)
    return T

def test():
    curve = {0:-1, 1:2, 2:0, 3:3, 4:-2, 5:1, 6:-3}
    tmt = {0:(3,6),1:(1,0),2:(1,0),3:(3,6),4:(5,6),5:(5,6),6:(6,6)}
    T = ComputeMergeTree(curve)
    print(tmt)
    print(T)

if __name__=="__main__":
    test()




