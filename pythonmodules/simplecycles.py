import networkx as NX
import DSGRN

def orderedExtrema(names,labeled_cycles):
    # need to write function based on paths of the form -m-, ---, M--, etc.
    paths = set([])
    for cyc in labeled_cycles:
        extrema = []
        for c in cyc:
            if "*" in c: raise ValueError("Debug: * in label.")
            elif "M" in c: extrema.append(names[c.index("M")]+" max")
            elif "m" in c: extrema.append(names[c.index("m")]+" min")
            else: pass
        paths.add(tuple(extrema))
    return paths

def findCycles(digraph):
    # graph is nx.DiGraph object
    cycles = NX.simple_cycles(digraph)
    cycles = [cyc+[cyc[0]] for cyc in cycles] #first element is left off of the end in simplecycles() output
    labeled_cycles = [[digraph.edge[u][v]["label"] for (u,v) in zip(cyc[:-1],cyc[1:])] for cyc in cycles]
    return labeled_cycles

def makeNXDigraph(domaingraph):
    ''' 
    Make networkx digraph in order to use the networkx library to find simple cycles.

    '''
    # get nodes
    nodes = range(domaingraph.digraph().size())
    # get edges
    edges=[ (i,a) for i in nodes for a in domaingraph.digraph().adjacencies(i) ]
    # attach labels to edges
    searchgraph = DSGRN.SearchGraph(domaingraph)
    MR = DSGRN.MatchingRelation(domaingraph.dimension())
    edgelabels = { (i,a) : MR.edge_labelstring(searchgraph.event(i,a)) for (i,a) in edges }
    # add nodes and edges to digraph
    G = NX.DiGraph()
    G.add_nodes_from(nodes)
    for edge,label in edgelabels.iteritems(): G.add_edge(edge[0],edge[1],label=label)
    return G

def findAllOrderedExtrema(networkfile=None,networkspec=None):
    if networkfile:
        network = DSGRN.Network(networkfile)
    elif networkspec:
        network = DSGRN.Network()
        network.assign(networkspec)
    else:
        raise ValueError("No input network.")
    names = [network.name(i) for i in range(network.size())]
    paramgraph = DSGRN.ParameterGraph(network)
    paths = set([])
    for paramind in range(paramgraph.size()):
        domaingraph = DSGRN.DomainGraph(paramgraph.parameter(paramind))
        G = makeNXDigraph(domaingraph)
        cycles = findCycles(G)
        paths.update(orderedExtrema(names,cycles))    
    return set(paths)

if __name__ == "__main__":
    netspec1 = "X : ~Z\nY : ~X\nZ : ~Y"
    netspec2 = "x1 : ~z1\ny1 : ~x1\nz1 : ~y1\nx2 : ~z2\ny2 : (~x1)(~x2)\nz2 : ~y2"
    netspec3 = "x1 : ~z1\ny1 : (~x1)(~x2)\nz1 : ~y1\nx2 : ~z2\ny2 : (~x1)(~x2)\nz2 : ~y2"
    netspec4 = "x1 : ~z1\ny : (~x1)(~x2)\nz1 : ~y\nx2 : ~z2\nz2 : ~y"
    print findAllOrderedExtrema(networkspec=netspec2)




    

