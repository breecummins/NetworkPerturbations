import networkx as nx
import dsgrn
import re


block_question=re.compile("[?]+")
DI_min=re.compile("DI")
ID_max=re.compile("ID")

def get_min_max(ipath):
    # First handle explicit extrema
    imin = [m.start(0) for m in DI_min.finditer(ipath)]
    imax = [m.start(0) for m in ID_max.finditer(ipath)]
    # Search for extrema in question mark blocks
    # Assume no extra extrema in D???I (i.e. there's exactly one min that occurs somewhere in ???)
    # If ?? extends to the beginning or end of the path, assume no extrema.
    # FIXME: if the path is a cycle, then could use extra info to get additional extrema,
    # for example ???ID??? must have a min somewhere in the ?? if it's a cycle.
    # However this leads to a bunch of special cases, so I'm ignoring it for now.
    for m in block_question.finditer(ipath):
        start, end = m.start(0), m.end(0)
        label1 = ipath[start-1] if start>0 else ""
        label2 = ipath[end] if end<len(ipath) else ""
        if label1+label2 == 'DI': imin += ipath[start:end]
        elif label1+label2 == 'ID': imax += ipath[start:end]
    return sorted(imin), sorted(imax)

def make_partial_order(graph,cycles,dim):
    '''
    Written assuming only one max and one min per variable.
    '''
    labeled_cycles = [[graph.node[c]["label"] for c in cyc] for cyc in cycles]
    for cyc in labeled_cycles:
        for i in range(dim):
            ipath = ''.join(c[i] for c in cyc)
            imin,imax = get_min_max(ipath)

    

