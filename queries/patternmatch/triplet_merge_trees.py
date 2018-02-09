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
    curve = {0:-1, 1:2, 2:0, 3:3, 4:-2, 5:1, 6:-3}
    tmt = {0:(3,6),1:(1,0),2:(1,0),3:(3,6),4:(5,6),5:(5,6),6:(6,6)}
    T = ComputeMergeTree2(curve)
    print(tmt)
    print(T)

if __name__=="__main__":
    test()




