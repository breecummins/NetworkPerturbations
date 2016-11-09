import networkx as nx
import DSGRN
import re
import intervalgraph as ig


block_question=re.compile("[?]+")
DI_min=re.compile("DI")
ID_max=re.compile("ID")

def get_min_max(ipath):
    # First handle explicit extrema
    imin = [m.start(0)+1 for m in DI_min.finditer(ipath)]
    imax = [m.start(0)+1 for m in ID_max.finditer(ipath)]
    # Now search for extrema in question mark blocks
    # Assume no extra extrema in D???I (i.e. there's exactly one min that occurs somewhere in ???)
    # If ?? extends to the beginning or end of the path, assume no extrema.
    # FIXME: if the path is a cycle, then could use extra info to get additional extrema,
    # for example ???ID??? must have a min somewhere in the ?? if it's a cycle.
    # However this leads to a bunch of special cases, so I'm ignoring it for now.
    for m in block_question.finditer(ipath):
        start, end = m.start(0), m.end(0)
        label1 = ipath[start-1] if start>0 else ""
        label2 = ipath[end] if end<len(ipath) else ""
        if label1+label2 == 'DI': imin += range(start,end+1)
        elif label1+label2 == 'ID': imax += range(start,end+1)
    return sorted(imin), sorted(imax)

def consecutive(l):
    # input list must be sorted low to high
    diff = [l[i+1]-l[i] for i in range(len(l)-1)]
    if any([d > 1 for d in diff]): return False
    else: return True

def make_partial_orders(graph,names):
    '''
    Written assuming only one max and one min per variable.
    graph is an nx.DiGraph object with meta-data "label" of the form {I,D,?}^len(names)
    names is a list of the gene names corresponding to each variable index
    '''
    cycles = nx.simplecycles(graph)
    cycles = [cyc+[cyc[0]] for cyc in cycles] #first element is left off of the end in simplecycles() output
    labeled_cycles = [[graph.node[c]["label"] for c in cyc] for cyc in cycles]
    partialorders = []
    for cyc in labeled_cycles:
        extrema = []
        for i,name in enumerate(names):
            ipath = ''.join(c[i] for c in cyc)
            imin,imax = get_min_max(ipath)
            if not consecutive(imin) or not consecutive(imax):
                raise ValueError("More than one maximum or minimum of variable {} in path.".format(name))
            else:
                extrema.append([name+" max",[imax[0],imax[-1]]])
                extrema.append([name+" min",[imin[0],imin[-1]]])
        partialorders.append(ig.IntervalGraph(extrema))
    return partialorders

def test():
    cyc = ["DDID","?DID","??ID","I?ID","??ID","??DD","?IDD","IIDD","IIDI","DIDI","DIDD","DIID","DDID"]
    extrema=[]
    for i in range(4):
        ipath = ''.join(c[i] for c in cyc)
        imin,imax = get_min_max(ipath)
        extrema.append([imin,imax])
    print extrema == [[[1,2,3],[9]],[[2,3,4,5,6],[12]],[[11],[5]],[[8],[10]]]
    minima = [ [ str(i)+ " min", [e[0][0],e[0][-1] ] ] for i,e in enumerate(extrema)  ]
    maxima = [ [ str(i)+ " max", [e[1][0],e[1][-1] ] ] for i,e in enumerate(extrema)  ]
    extrema = minima + maxima
    graph = ig.IntervalGraph(extrema).transitive_reduction()
    answer = {"0 min":["2 max"],"2 max":["3 min"],"1 min":["3 min"],"3 min":["0 max"],"0 max":["3 max"],"3 max":["2 min"],"2 min":["1 max"],"1 max":[]}
    for v in graph.vertices():
        # print graph.vertex_label(v), [graph.vertex_label(w) for w in  graph.adjacencies(v)]
        print answer[graph.vertex_label(v)] == [graph.vertex_label(w) for w in  graph.adjacencies(v)]


if __name__ == "__main__":
    test()



    

