import DSGRN
import networkx as NX
import sys, time

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
        # print len(cyc),len(extrema)      
        paths.add(tuple(extrema))
    return paths

def findCycles(digraph):
    # graph is nx.DiGraph object
    cycles = NX.simple_cycles(digraph)
    cycles = [cyc+[cyc[0]] for cyc in cycles] #first element is left off of the end in simplecycles() output
    labeled_cycles = set([tuple([digraph.edge[u][v]["label"] for (u,v) in zip(cyc[:-1],cyc[1:])]) for cyc in cycles])
    return labeled_cycles

def makeNXDigraph(domaingraph,nodes=None,edges=None):
    ''' 
    Make networkx digraph in order to use the networkx library to find simple cycles.

    '''
    if not nodes:
        # get nodes
        nodes = range(domaingraph.digraph().size())
    if not edges:
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

def makeMasterCycles(cycle):
    return [ tuple(list(cycle[n:]) + list(cycle[:n])) for n in range(len(cycle)) ]


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
    mastercycles = set([])
    for paramind in range(paramgraph.size()):
        domaingraph = DSGRN.DomainGraph(paramgraph.parameter(paramind))
        cycles = findCycles(makeNXDigraph(domaingraph))
        for cyc in cycles:
            # check for identical cycles at different starting nodes
            if cyc not in mastercycles:
                mastercycles.update(makeMasterCycles(cyc))
                paths.update(orderedExtrema(names,cycles))  
    return set(paths)

def findAllOrderedExtrema_Morsesets(networkfile=None,networkspec=None):
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
    mastercycles = set([])
    start = time.time()
    for paramind in range(paramgraph.size()):
        if time.time()-start >= 2:
            print "{} / {} parameters analyzed\n".format(paramind,paramgraph.size())
            start = time.time()
        domaingraph = DSGRN.DomainGraph(paramgraph.parameter(paramind))
        morsedecomposition = DSGRN.MorseDecomposition(domaingraph.digraph())
        for i in range(0,morsedecomposition.poset().size()):
            ms = morsedecomposition.morseset(i)
            if len(ms) > 1:
                morseedges = [ (i,a) for a in domaingraph.digraph().adjacencies(i) if a in ms ]
                cycles = findCycles(makeNXDigraph(domaingraph,ms,morseedges))
                try: 
                    C = max(len(c) for c in cycles)
                    if C > len(ms):
                        print "morse set: {}, max cycle: {}".format(len(ms),C)
                except: pass
                extrema  = orderedExtrema(names,cycles)
                for e in extrema:
                    # check for identical cycles at different starting nodes
                    if e not in mastercycles:
                        mastercycles.update(makeMasterCycles(e))
                        paths.add( e ) 
                        # print paths 

        # if len(paths) > 10000:
        #     # for p in paths:
        #     #     print p
        #     print "\n\n"
        #     print len(paths)
        #     print "\n\n"
        #     print len(mastercycles)
        #     print "\n\n"
        #     print max([len(p) for p in paths])
        #     sys.exit()  
    return set(paths)

if __name__ == "__main__":
    import sys

    netspec0 = "X : ~Z\nY : ~X\nZ : ~Y"
    netspec1 = "x1 : ~z1\ny1 : ~x1\nz1 : ~y1\nx2 : ~z2\ny2 : (~x1)(~x2)\nz2 : ~y2"
    netspec2 = "x1 : ~z1\ny1 : (~x1)(~x2)\nz1 : ~y1\nx2 : ~z2\ny2 : (~x1)(~x2)\nz2 : ~y2"
    netspec3 = "x1 : ~z1\ny : (~x1)(~x2)\nz1 : ~y\nx2 : ~z2\nz2 : ~y"

    num = sys.argv[1]
    ns = eval("netspec" + num)
    print "\n" + ns + "\n\n"
    sys.stdout.flush()

    print len(findAllOrderedExtrema_Morsesets(networkspec=ns))




    

