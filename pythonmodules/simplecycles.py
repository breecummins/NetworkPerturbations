import networkx as nx
import dsgrn
import re


block_question=re.compile("[?]+")
ID=re.compile("ID")
DI=re.compile("DI")

def get_min_max(ipath):
    # First handle explicit extrema
    imin = [m.start(0) for m in DI.finditer(ipath)]
    imax = [m.start(0) for m in ID.finditer(ipath)]
    # Search for extrema in question mark blocks
    # Assume no extra extrema in D???I (i.e. there's exactly one min that occurs somewhere in ???)
    # If ?? extends to the beginning or end of the path, assume no extrema.
    # FIXME: if the path is a cycle, then could use extra info to get additional extrema,
    # for example ???ID??? must have a min somewhere in the ?? if it's a cycle.
    # However this leads to a bunch of special cases, so I'm ignoring it for now.
    for m in block_question.finditer(ipath):
        start, end = m.start(0), m.end(0)
        label1, label2 = "",""
        if start > 0: label1 = ipath[start-1]
        if end < len(ipath)-1: label2 = ipath[end+1]
        if label1 == 'D' and label2 == 'I':
            imin += list(ipath[start:end])
        elif label1 == 'I' and label2 == 'D':
            imax += list(ipath[start:end])

