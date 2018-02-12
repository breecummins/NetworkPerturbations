# reference: Dmitriy Smirnov and Dmitriy Morozov Chapter 1 Triplet Merge Trees
# people.csail.mit.edu/smirnov/publications/tmt.pdf
# Algorithms 1 & 2

def ComputeMergeTree(curve):
    '''
    :param curve: dict with times keying function values
    :return: triplet merge tree representation --
             a dict with a time keying a tuple of times, T[u] = (s,v),
             where u obtains label v at time s (branch decomposition)

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
    sorted_verts = [a for (a,b) in sorted(curve.iteritems(), key=lambda (k,v): v)]
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


def test():
    curve = {0:-2, 1:2, 2:0, 3:3, 4:-4, 5:1, 6:-7}
    tmt = {0:(3,6),1:(1,0),2:(1,0),3:(3,6),4:(5,6),5:(5,6),6:(6,6)}
    T = ComputeMergeTree(curve)
    print(tmt)
    print(T)

    import numpy as np

    def normalize(cur):
        times = [t for t in cur]
        vals = np.array([cur[t] for t in times])
        nvals = (vals - float(np.min(vals)))/(np.max(vals)-np.min(vals)) - 0.5
        return dict( (t,n) for (t,n) in zip(times,nvals) )

    norm_curve = normalize(curve)
    print(ComputeMergeTree(norm_curve))

    tMt = {0:(0,3),1:(2,3),2:(2,3),3:(3,3),4:(4,3),5:(4,3),6:(6,3)}
    norm_curve_rev = dict( (t,-1*n) for (t,n) in norm_curve.iteritems())
    print("\nmaxes\n")
    print(tMt)
    print(ComputeMergeTree(norm_curve_rev))
    curve_rev = dict( (t,-1*n) for (t,n) in curve.iteritems())
    print(curve_rev)
    print(ComputeMergeTree(curve_rev))



    import matplotlib.pyplot as plt

    # times = [t for t in norm_curve]
    # vals = np.array([norm_curve[t] for t in times])
    times_rev = [t for t in curve_rev]
    vals_rev = np.array([curve_rev[t] for t in times_rev])

    # plt.plot(times,vals,color='r')
    # plt.hold('on')
    plt.plot(times_rev,vals_rev,color='b')
    plt.show()



if __name__=="__main__":
    test()




