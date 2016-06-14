import random
from functools import partial
# graph is an intervalgraph.Graph object

##############################################################################
# Low level helper functions for managing network nodes
##############################################################################

def constructNetworkNodeList(graph):
    # get list of network labels from graph
    # graph.vertices is an unordered set, need to impose order for my functionality
    # need network names to choose new nodes/edges
    # need network indices to add nodes/edges to graph
    networknodelist = [(v,graph.vertex_label(v)) for v in graph.vertices()] 
    networknodenames = [n[1] for n in networknodelist]
    networknodeindices = [n[0] for n in networknodelist]
    return networknodenames,networknodeindices

def filterNodeList(networknodenames,nodelist):
    nodelist = [ n for n in nodelist if n not in networknodenames ]
    if not nodelist:
        raise ValueError("No new nodes may be added. Aborting network creation early.")
    return nodelist

##################################################################################################
# All "get" functions return nodes and/or edges meeting criteria, or throw an error if they can't.
##################################################################################################

def getRandomHalfEdge(n):
    # pick incoming or outgoing index plus regulation
    node = random.randrange(n)
    regbool = random.randrange(2)
    reg = 'a'*regbool + 'r'*(not regbool)
    return node,reg

def getRandomEdge(networknodenames):
    # make random named edge; may or may not be in existing graph
    n = len(networknodenames)
    startnode, reg = getRandomHalfEdge(n)
    endnode = random.randrange(n)
    return (networknodenames[startnode],networknodenames[endnode],reg)

def getObjectFromFilteredList(masterlist):
    # masterlist = (filtered) nodelist or edgelist (e.g. get rid of existing network objects, restrict to subset of nodes, ignore negative self-loops)
    # pick randomly from list
    if not masterlist:
        raise ValueError("No more objects to choose. Aborting network creation early.")
    return masterlist[random.randrange(len(masterlist))]

def getNodeAndConnectingEdgesFromLists(networknodenames,nodelist,edgelist):
    # get a node from provided list and in- and out-edges to the existing network from a list
    # random edges if edgerank = None, ordered edges if edgerank is integer
    # random node if noderank = None, ordered node if noderank is integer

    def filterEdges(nodelabel):
    # filter edgelist via nodelabel, so that only edges to and from nodelabel to the network exist
    # nodelabel is not in networknodenames
    # edge list is list of all allowed edges to add to network
    inedges=[]
    outedges=[]
    for edge in edgelist:
        # note: we do not have to test for negative self-loops because nodelabel is not in networknodenames
        if edge[0] in networknodenames and edge[1] == nodelabel:
            inedges.append(edge)
        elif edge[0] == nodelabel and edge[1] in networknodenames:
            outedges.append(edge)
    return inedges,outedges

    def generateCandidate(thisnodelist):
        # propose a node and connecting edges
        newnodelabel = getObjectFromFilteredList(thisnodelist)
        try:
            inedges,outedges = filterEdges(newnodelabel)
            inedge = getObjectFromFilteredList(inedges)
            outedge = getObjectFromFilteredList(outedges)
            return newnodelabel,inedge,outedge
        except:
            return newnodelabel,None,None

    # filter nodelist
    nodelist = filterNodeList(networknodenames,nodelist)
    # get node and connecting edges
    newnodelabel,inedge,outedge = generateCandidate(nodelist)
    while inedge is None or outedge is None:
        nodelist.remove(newnodelabel)
        if not nodelist: # final termination condition: if all new nodes have empty edge lists, abort
            raise ValueError("No new nodes may be added. Aborting network creation early.")
        newnodelabel,inedge,outedge = generateCandidate(nodelist)
    return newnodelabel,inedge,outedge

##############################################################################
# All "add" functions take a graph object and return a modified graph object.
##############################################################################

def addEdge(graph,edgelist=()):
    # if no edgelist, then a random edge is added to the network
    # if edgelist is specified, a random choice is made from the filtered edgelist (filtered against networknodelist)

    def isNegSelfLoop(edge):
        # check for negative self-loops
        if edge[0]==edge[1] and edge[2]=='r':
            return True
        else:
            return False

    # exclude trivial graphs
    networknodenames,networknodeindices = constructNetworkNodeList(graph)
    n = len(networknodenames)
    if n < 2: 
        raise ValueError("Trivial graph, cannot add edges. Aborting network creation early.")  

    # transform graph into a list of edge tuples using vertex labels instead of vertex indices
    graph_named_edges = [(graph.vertex_label(v),graph.vertex_label(e),graph.edge_label(v,e)) for v in graph.vertices() for a in graph.adjacencies(v) for e in a] 

    # get a new edge
    if edgelist:
        edgelist = [e for e in edgelist if e[0] in networknodenames and e[1] in networknodenames and e not in graph_named_edges and not isNegSelfLoop(e)]
        newedge = getObjectFromFilteredList(edgelist)
    else:
        newedge = getRandomEdge(networknodenames)  
        while newedge in graph_named_edges or isNegSelfLoop(newedge):
            # will terminate for nontrivial (n>1) graphs, because not all possible edges can exist simultaneously in a nontrivial network
            newedge = getRandomEdge(networknodenames)  

    # add the new edge to the graph
    startnode = networknodeindices[networknodenames.index(newedge[0])]
    endnode = networknodeindices[networknodenames.index(newedge[1])]
    if endnode in graph.adjacencies(startnode):
        graph.change_edge_label(startnode,endnode,newedge[2])
    else:
        graph.add_edge(startnode,endnode,label=newedge[2])
    return graph 

def addNodeAndConnectingEdges(graph,nodelist=(),edgelist=()):
    # choose new node and connecting edges
    # if nodelist, choose random node from a (filtered) list
    # if edgelist, choose random in- and out-edges from a (filtered) list
    # if no edgelist, choose in- and out-edges randomly without a list
    # if no nodelist, make up a name for a new node (and add random edges sans edgelist)

    def makeupNode(networknodenames):
        # make unique node name
        newnodelabel = 'x'+str(n)
        c=1
        while newnodelabel in networknodenames:
            # must terminate because networknodenames is finite
            newnodelabel = 'x'+str(n+c)
            c+=1
        return newnodelabel

    networknodenames,networknodeindices = constructNetworkNodeList(graph)
    n = len(networknodenames)

    if not nodelist:
        newnodelabel = makeupNode(networknodenames)        
        # pick random incoming and outgoing edges for n from network node list
        innode,inreg = getRandomHalfEdge(n)
        outnode,outreg = getRandomHalfEdge(n)
    elif not edgelist:
        nodelist = filterNodeList(networknodenames,nodelist) # do not filter this earlier, could get nodelist=() which is semantically important as an input argument
        newnodelabel = getObjectFromFilteredList(nodelist)
        # pick random incoming and outgoing edges for n from network node list
        innode,inreg = getRandomHalfEdge(n)
        outnode,outreg = getRandomHalfEdge(n)
    else:
        newnodelabel,inedge,outedge = getNodeAndConnectingEdgesFromLists(networknodelist,nodelist,edgelist)
        innode = networknodeindices[networknodenames.index(inedge[0])]
        outnode = networknodeindices[networknodenames.index(outedge[1])]
        inreg = inedge[2]
        outreg = outedge[2]
    # add to graph
    graph.add_vertex(n,label=newnodelabel)
    graph.add_edge(innode,n,label=inreg)
    graph.add_edge(n,outnode,label=outreg)
    return graph


##############################################################################
# Network perturbation call. Generally the only function used externally.
##############################################################################

def perturbNetwork(graph,nodelist,edgelist):
    keepgoing = 1
    while keepgoing:
        edge = getRandomInt(2)
        if edge:
            graph = addEdge(graph,edgelist)
        else:
            graph = addNodeAndConnectingEdges(graph,nodelist,edgelist)
        keepgoing = getRandomInt(2)
    return graph

