import random
# graph is an intervalgraph.Graph object

##############################################################################
# Low level helper functions
##############################################################################

def constructNamedEdgesFromGraph(graph):
    # transform graph into a list of edge tuples using vertex labels instead of vertex indices
    graph_named_edges = [(graph.vertex_label(v),graph.vertex_label(e),graph.edge_label(v,e)) for v in graph.vertices() for a in graph.adjacencies(v) for e in a]
    return graph_named_edges

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

##############################################################################
# All "get" function return nodes and/or edges, or throw an error if they can't.
##############################################################################

def getNewRandomEdge(graph_named_edges,networknodelist,edgelist=()):
    # get a new, not-already-existing edge to add to the graph; optionally pull it from an allowed list
    # graph_named_edges (from constructNamedEdgesFromGraph(graph)) is a list of named adjacencies in the format of edgelist
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

def getRandomInOrOutEdgeFromList(nodelabel,networknodelist,newnodeedgelist,isinedge=True):
    # nodelabel is not in networknodelist
    # newnodeedgelist is non-empty list of edge names between nodelabel and the nodes in networknodelist
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

def getOrderedEdge(graph_named_edges,edgelist,rank):
    # graph_named_edges (from constructNamedEdgesFromGraph(graph)) is a list of named adjacencies in the format of edgelist
    # edge list is list of edges to add to network
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

def getRandomNodeFromList(networknodelist,nodelist):
    # check if it is possible to choose a new node (ensures while loop terminates)
    if not set(nodelist).difference(networknodelist):
        raise ValueError("No more nodes to choose. Aborting network creation early.")
    n = len(nodelist)
    index = generateRandomInt(n)
    while nodelist[index] in networknodelist:
        index = generateRandomInt(n)
    return nodelist[index]

def getRandomNodeFromListAndAllowedEdges(graph_named_edges,networknodelist,nodelist,edgelist):
    # get a random node from provided list and the potential in- and out-edges to the existing network
    def generateCandidate():
        newnodelabel = getRandomNodeFromList(networknodelist,nodelist)
        inedges,outedges = filterEdges(newnodelabel,networknodelist,edgelist)
        return newnodelabel,inedges,outedges
    newnodelabel,inedges,outedges = generateCandidate()
    tried_labels=set()
    remaining_labels=set(nodelist).difference(networknodelist)
    while not inedges or not outedges:
        tried_labels.add(newnodelabel)
        if tried_labels == remaining_labels: # if all new nodes have empty edge lists, abort
            raise ValueError("No new nodes with non-empty edge lists. Aborting network creation early.")
        newnodelabel,inedges,outedges = generateCandidate()
    return newnodelabel,inedges,outedges

##############################################################################
# All "add" functions take a graph object and return a modified graph object.
##############################################################################

def addNode(graph,newnodelabel,innode,inreg,outnode,outreg):
    # helper function for all "add" functions that add a node, ordered or random
    n = len(graph.vertices())
    # the new node will have index n
    graph.add_vertex(n,label=newnodelabel)
    graph.add_edge(innode,n,label=inreg)
    graph.add_edge(n,outnode,label=outreg)
    return graph

def addRandomEdgeOptionalList(graph,edgelist=()):
    networknodelist = constructNetworkNodeList(graph)
    graph_named_edges = constructNamedEdgesFromGraph(graph)
    newedge = getNewRandomEdge(graph_named_edges,edgelist)
    startnode = networknodelist.index[newedge[0]]
    endnode = networknodelist.index[newedge[1]]
    if endnode in graph.adjacencies(startnode):
        graph.change_edge_label(startnode,endnode,newedge[2])
    else:
        graph.add_edge(startnode,endnode,label=newedge[2])
    return graph 

def addNewNodeAndRandomEdgesNoList(graph,networknodelist=None,newnodelabel=None):
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

def addRandomNodeFromListAndRandomEdgesNoList(graph,nodelist):
    networknodelist = constructNetworkNodeList(graph)
    newnodelabel = getRandomNodeFromList(networknodelist,nodelist)
    graph = addNewNodeAndRandomEdgesNoList(graph,networknodelist,newnodelabel)
    return graph

def addOrderedNodeRandomEdgesNoList(graph,nodelist,noderank):
    networknodelist = constructNetworkNodeList(graph)
    newnodelabel = getOrderedNode(networknodelist,nodelist,noderank)
    graph = addNewNodeAndRandomEdgesNoList(graph,networknodelist,newnodelabel)
    return graph

def addRandomNodeAndEdgesFromLists(graph,nodelist,edgelist):
    networknodelist = constructNetworkNodeList(graph)
    graph_named_edges = constructNamedEdgesFromGraph(graph)
    newnodelabel,inedges,outedges = getRandomNodeFromListAndAllowedEdges(graph_named_edges,networknodelist,nodelist,edgelist)
    innode,inreg = getRandomInOrOutEdgeFromList(newnodelabel,networknodelist,inedges,isinedge=True)
    outnode,outreg = getRandomInOrOutEdgeFromList(newnodelabel,networknodelist,outedges,isinedge=False)
    graph = addNode(graph,newnodelabel,innode,inreg,outnode,outreg)
    return graph

def addRandomNodeOrderedEdges(graph,nodelist,edgelist,edgerank):
    networknodelist = constructNetworkNodeList(graph)
    graph_named_edges = constructNamedEdgesFromGraph(graph)
    newnodelabel,inedges,outedges = getRandomNodeFromListAndAllowedEdges(graph_named_edges,networknodelist,nodelist,edgelist)
    inedge = getOrderedEdge(graph_named_edges,inedges,edgerank)
    outedge = getOrderedEdge(graph_named_edges,outedges,edgerank)
    graph = addNode(graph,newnodelabel,inedge[0],inedge[2],outedge[1],outedge[2])
    return graph

def addOrderedNodeRandomEdgesFromList(graph,nodelist,edgelist,noderank):
    networknodelist = constructNetworkNodeList(graph)
    newnodelabel = getOrderedNode(networknodelist,nodelist,noderank)
    graph_named_edges = constructNamedEdgesFromGraph(graph)
    inedges,outedges = filterEdges(newnodelabel,networknodelist,edgelist)
    if not inedges or not outedges:
        raise ValueError("No appropriate edges in list. Aborting network creation early.")
    innode,inreg = getRandomInOrOutEdgeFromList(newnodelabel,networknodelist,inedges,isinedge=True)
    outnode,outreg = getRandomInOrOutEdgeFromList(newnodelabel,networknodelist,outedges,isinedge=False)
    graph = addNode(graph,newnodelabel,innode,inreg,outnode,outreg)
    return graph

def addOrderedNodeOrderedEdges(graph,nodelist,edgelist,noderank,edgerank):
    pass
    

