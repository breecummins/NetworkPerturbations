import random
# graph is an intervalgraph.Graph object

##############################################################################
# Low level helper functions
##############################################################################

def constructNetworkNodeList(graph):
    # get list of network labels from graph
    networknodelist = [graph.vertex_label(v) for v in graph.vertices()]
    return networknodelist

def isNegSelfLoop(edge):
    # check for negative self-loops
    if edge[0]==edge[1] and edge[2]=='r':
        return True
    else:
        return False

def generateRandomInt(n):
    return random.randrange(n)

def generateRandomEdge(networknodelist):
    # make random edge; may or may not be in existing graph
    n = len(networknodelist)
    startnode = generateRandomInt(n)
    endnode = generateRandomInt(n)
    regbool = generateRandomInt(2)
    newedgereg = 'a'*regbool + 'r'*(not regbool)
    return (networknodelist[startnode],networknodelist[endnode],newedgereg)

def filterEdges(nodelabel,networknodelist,edgelist):
    # filter edgelist via nodelabel, so that only edges to and from nodelabel to the network exist
    # nodelabel is not in networknodelist
    # edge list is list of all allowed edges to add to network
    inedges=[]
    outedges=[]
    for edge in edgelist:
        if edge[0] in networknodelist and edge[1] == nodelabel:
            inedges.append(edge)
        elif edge[0] == nodelabel and edge[1] in networknodelist:
            outedges.append(edge)
    return inedges,outedges

#########################################################################################
# All "get" function return selected nodes and/or edges, or throw an error if they can't.
#########################################################################################

def getNewRandomEdge(graph_named_edges,networknodelist,edgelist=()):
    # get a new, not-already-existing edge to add to the graph; optionally pull it from an allowed list
    # graph_named_edges is a list of named adjacencies in the format of edgelist
    # edgelist is list of allowable edges; empty means pick random edge to add to network
    n = len(networknodelist)
    if n < 2: # exclude trivial graphs for second while loop
        raise ValueError("Trivial graph, cannot add edges. Aborting network creation early.")  
    edge = generateRandomEdge(networknodelist)  
    if edgelist: 
        tried_edges=set()
        while edge in graph_named_edges or isNegSelfLoop(edge) or edge not in edgelist:
            # check last-ditch termination condition: max # of edges = 2 signs of edge between any two nodes and self-loops allowed
            # n choose 2 with replacement = (n-r+1)!/r!(n-1)! = n(n+1)/2 when r=2; multiply by two allowed edge signs = n(n+1)
            # (cannot use subset test as in getRandomInOrOutEdgeFromList, because this edgelist is not filtered to just network nodes)
            tried_edges.add(edge)
            if len(tried_edges) == n*(n+1): 
                raise ValueError("All edges tested and none work. Aborting network creation early.")
            edge = generateRandomEdge(networknodelist)  
    else:
        while edge in graph_named_edges or isNegSelfLoop(edge):
            # will terminate for nontrivial (n>1) graphs, because either there are missing edges in the graph, or there are non-loop edges where you can change the sign of an edge
            edge = generateRandomEdge(networknodelist)  
    return edge

def getRandomInOrOutEdgeFromList(nodelabel,networknodelist,edgelist,isinedge=True):
    # nodelabel is not in networknodelist (existing nodes in network)
    # edgelist is allowed edges
    inedges,outedges = filterEdges(nodelabel,networknodelist,edgelist)
    if isinedge:
        if inedges:
            newnodeedgelist = inedges
        else:
            raise ValueError("No appropriate edges in list. Aborting network creation early.")
    else:
        if outedges:
            newnodeedgelist = outedges
        else:
            raise ValueError("No appropriate edges in list. Aborting network creation early.")
    (_,othernode,newedgereg) = generateRandomEdge(networknodelist)
    edge = (othernode,nodelabel,newedgereg) if isinedge else (nodelabel,othernode,newedgereg)
    tried_edges=set()
    while edge not in newnodeedgelist:
        tried_edges.add(edge)
        if set(edgelist).issubset(tried_edges): # if all edges tried, terminate loop
            raise ValueError("All edges tested and none work. Aborting network creation early.")
        (_,othernode,newedgereg) = generateRandomEdge(networknodelist)
        edge = (othernode,nodelabel,newedgereg) if isinedge else (nodelabel,othernode,newedgereg)
    return othernode,newedgereg

def getRandomNodeFromList(networknodelist,nodelist):
    # check if it is possible to choose a new node (ensures while loop terminates)
    candidates = list(set(nodelist).difference(networknodelist))
    if not candidates:
        raise ValueError("No more nodes to choose. Aborting network creation early.")
    index = generateRandomInt(len(candidates))
    return candidates[index]

def getRandomNodeAndRandomConnectingEdgesFromLists(networknodelist,nodelist,edgelist):
    # get a random node from provided list and the potential in- and out-edges to the existing network

    def generateCandidate():
        newnodelabel = getRandomNodeFromList(networknodelist,nodelist)
        try:
            innode,inreg = getRandomInOrOutEdgeFromList(newnodelabel,networknodelist,edgelist,isinedge=True)
            outnode,outreg = getRandomInOrOutEdgeFromList(newnodelabel,networknodelist,edgelist,isinedge=False)
            return newnodelabel,innode,inreg,outnode,outreg
        except:
            return newnodelabel,None,None,None,None
        
    newnodelabel,innode,inreg,outnode,outreg = generateCandidate()
    tried_labels=set()
    remaining_labels=set(nodelist).difference(networknodelist)
    while innode is None or outnode is None:
        tried_labels.add(newnodelabel)
        if tried_labels == remaining_labels: # if all new nodes have empty edge lists, abort
            raise ValueError("No new nodes with non-empty edge lists. Aborting network creation early.")
        newnodelabel,innode,inreg,outnode,outreg = generateCandidate()
    return newnodelabel,innode,inreg,outnode,outreg

def getRandomNodeAndOrderedConnectingEdgesFromLists(networknodelist,nodelist,edgelist,rank):
    # get a random node from provided list and the potential in- and out-edges to the existing network

    def generateCandidate():
        newnodelabel = getRandomNodeFromList(networknodelist,nodelist)
        inedges,outedges = filterEdges(newnodelabel,networknodelist,edgelist)
        try:
            inedge = getOrderedEdge((),inedges,rank)
            outedge = getOrderedEdge((),outedges,rank)
            return newnodelabel,inedge,outedge
        except:
            return newnodelabel,None,None
        
    newnodelabel,inedge,outedge = generateCandidate()
    tried_labels=set()
    remaining_labels=set(nodelist).difference(networknodelist)
    while inedge is None or outedge is None:
        tried_labels.add(newnodelabel)
        if tried_labels == remaining_labels: # if all new nodes have empty edge lists, abort
            raise ValueError("No new nodes with non-empty edge lists. Aborting network creation early.")
        newnodelabel,inedge,outedge = generateCandidate()
    return newnodelabel,inedge,outedge

def getOrderedEdge(graph_named_edges,edgelist,rank):
    # graph_named_edges (from constructNamedEdgesFromGraph(graph)) is a list of named adjacencies in the format of edgelist
    # edge list is list of edges to add to a pre-existing network (i.e. edges are filtered so that only network nodes are represented)
    numedges = 0
    for edge in edgelist:
        if edge not in graph_named_edges:
            numedges+=1
        if numedges==rank:
            return edge
    raise ValueError("Too many edge ranks requested. Aborting network creation early.")

def getOrderedNode(networknodelist,nodelist,rank):
    numnodes = 0
    for node in nodelist:
        if node not in networknodelist:
            numnodes+=1
        if numnodes==rank:
            return node
    raise ValueError("Too many node ranks requested. Aborting network creation early.")

##############################################################################
# All "add" functions take a graph object and return a modified graph object.
##############################################################################

def addEdge(graph,edgelist=(),edgerank=None):
    # if neither edgelist nor edgerank is specified, then a random edge is added to the network
    # if edgelist is specified, a random choice is made from the filtered edgelist (filtered against networknodelist)
    # if edgerank is specified, an ordered edge is taken from the filtered edgelist (filtered against networknodelist)
    networknodelist = constructNetworkNodeList(graph)
    # transform graph into a list of edge tuples using vertex labels instead of vertex indices
    graph_named_edges = [(graph.vertex_label(v),graph.vertex_label(e),graph.edge_label(v,e)) for v in graph.vertices() for a in graph.adjacencies(v) for e in a]    
    if edgerank is not None:
        allowededges = []
        for e in edgelist:
            if e[0] in networknodelist and e[1] in networknodelist:
                allowededges.append(e)
        newedge = getOrderedEdge(graph_named_edges,allowededges,edgerank)
    else:
        newedge = getNewRandomEdge(graph_named_edges,networknodelist,edgelist)
    startnode = networknodelist.index[newedge[0]]
    endnode = networknodelist.index[newedge[1]]
    if endnode in graph.adjacencies(startnode):
        graph.change_edge_label(startnode,endnode,newedge[2])
    else:
        graph.add_edge(startnode,endnode,label=newedge[2])
    return graph 

def addNode(graph,newnodelabel,innode,inreg,outnode,outreg):
    # helper function for all "add" functions that add a node, ordered or random
    n = len(graph.vertices())
    # the new node will have index n
    graph.add_vertex(n,label=newnodelabel)
    graph.add_edge(innode,n,label=inreg)
    graph.add_edge(n,outnode,label=outreg)
    return graph

def addNodeAndRandomEdges(graph,networknodelist=None,newnodelabel=None):
    # can use this function even when there is no nodelist from which to pull nodes
    # if networknodelist has not been calculated, do so now
    # if newnodelabel is not specified, add a generic 'x' node
    if networknodelist is None:
        networknodelist = constructNetworkNodeList(graph)
    if newnodelabel is None:
        newnodelabel = 'x'+str(len(networknodelist))
    # pick outgoing and incoming edges for n from the existing network (i.e. don't pick node n)
    (innode,_,inreg) = generateRandomEdge(networknodelist)
    # pick an outgoing edge for n from the existing network
    (_,outnode,outreg) = generateRandomEdge(networknodelist)
    graph = addNode(graph,newnodelabel,innode,inreg,outnode,outreg)
    return graph

def addNodeFromListAndRandomEdges(graph,nodelist,noderank=None):
    # pick a node from a list
    # if noderank is specified, choose an ordered node
    # otherwise choose a random node from the list
    # in both cases, connect the node to the network with random edges
    networknodelist = constructNetworkNodeList(graph)
    if noderank is not None:
        newnodelabel = getOrderedNode(networknodelist,nodelist,noderank)
    else:
        newnodelabel = getRandomNodeFromList(networknodelist,nodelist)
    graph = addNodeAndRandomEdges(graph,networknodelist,newnodelabel)
    return graph

# note addNodeAndEdgesFromList is missing; this is because we REQUIRE a node name in the case where we have named edges; cannot pick random edges and then add nodes

def addRandomNodeFromListAndEdgesFromList(graph,nodelist,edgelist,edgerank=None):
    # pick a random node from a list
    # if edgerank is specified, choose ordered edges to connect the node to the network
    # otherwise choose random edges from a list of allowed edges
    networknodelist = constructNetworkNodeList(graph)
    if edgerank is not None:
        newnodelabel,inedge,outedge = getRandomNodeAndOrderedConnectingEdgesFromLists((),networknodelist,nodelist,edgelist,edgerank)
    else:
        newnodelabel,innode,inreg,outnode,outreg = getRandomNodeAndRandomConnectingEdgesFromLists((),networknodelist,nodelist,edgelist)
    graph = addNode(graph,newnodelabel,innode,inreg,outnode,outreg)
    return graph

def addOrderedNodeFromListAndEdgesFromList(graph,nodelist,edgelist,noderank,edgerank=None):
    # get an ordered node from a list
    # if edgerank is specified, choose ordered edges to connect the node to the network
    # otherwise choose random edges from a list of allowed edges
    networknodelist = constructNetworkNodeList(graph)
    newnodelabel = getOrderedNode(networknodelist,nodelist,noderank)
    if edgerank is not None:
        inedges,outedges = filterEdges(newnodelabel,networknodelist,edgelist)   
        inedge = getOrderedEdge((),inedges,edgerank)
        outedge = getOrderedEdge((),outedges,edgerank)
        graph = addNode(graph,newnodelabel,inedge[0],inedge[2],outedge[1],outedge[2])
    else:
        innode,inreg = getRandomInOrOutEdgeFromList(newnodelabel,networknodelist,edgelist,isinedge=True)
        outnode,outreg = getRandomInOrOutEdgeFromList(newnodelabel,networknodelist,edgelist,isinedge=False)
        graph = addNode(graph,newnodelabel,innode,inreg,outnode,outreg)
    return graph
