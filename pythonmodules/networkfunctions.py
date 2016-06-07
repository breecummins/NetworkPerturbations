import random
# graph is an intervalgraph.Graph object

def getRandomInt(n):
    return random.randrange(n)

def getNamedEdgesInGraph(graph):
    graph_named_edges = [(graph.vertex_label(v),graph.vertex_label(e),graph.edge_label(v,e)) for v in graph.vertices() for a in graph.adjacencies(v) for e in a]
    return graph_named_edges

def getNetworkNodeList(graph):
    networknodelist = [graph.vertex_label(v) for v in graph.vertices()]
    return networknodelist

def isUnsignedEdgeInGraph(graph_named_edges,startnode,endnode):
    for edge in graph_named_edges:
        if edge[0] == startnode and edge[1] == endnode:
            return edge[2]
    return False

def isSignedEdgeInGraph(graph_named_edges,edge):
    if edge in graph_named_edges:
        return True
    else:
        return False        

def isNegSelfLoop(edge):
    if edge[0]==edge[1] and edge[2]=='r':
        return True
    else:
        return False

def generateRandomEdge(networknodelist):
    n = len(networknodelist)
    startnode = getRandomInt(n)
    endnode = getRandomInt(n)
    regbool = getRandomInt(2)
    newedgereg = 'a'*regbool + 'r'*(not regbool)
    return (networknodelist[startnode],networknodelist[endnode],newedgereg)

def sanityCheckNodeList(networknodelist,nodelist):
    # check if it is possible to choose a new node
    # used to sanity check inputs to while loops over node list
    if not set(nodelist).difference(networknodelist):
        raise ValueError("Warning: No more nodes to choose. Aborting network creation early.")

def sanityCheckEdgeList(edgelist,tried_edges):
    # check if all edges have been tried
    # used to sanity check inputs to while loops over edge list
    if set(edgelist).issubset(tried_edges):
        raise ValueError("Warning: All edges tested and none work. Aborting network creation early.")

def getNewRandomEdge(graph_named_edges,networknodelist,networkedgelist=()):
    # graph_named_edges (from getNamedEdgesInGraph(graph)) is a list of named adjacencies in the format of edgelist
    # networkedgelist is list of containing edge names between nodes in networknodelist; empty means pick random edge in network
    if len(networknodelist) < 2: # exclude trivial graphs for second while loop
        raise ValueError("Warning: Trivial graph, cannot add edges. Aborting network creation early.")  
    edge = generateRandomEdge(networknodelist)  
    if edgelist: 
        tried_edges=set()
        while edge in graph_named_edges or isNegSelfLoop(edge) or edge not in networkedgelist:
            tried_edges.add(edge)
            sanityCheckEdgeList(networkedgelist,tried_edges)
            edge = generateRandomEdge(networknodelist)  
    else:
        while edge in graph_named_edges or isNegSelfLoop(edge):
            # will terminate for nontrivial (n>1) graphs
            edge = generateRandomEdge(networknodelist)  
    return edge

def getRandomInOrOutEdgeFromList(nodelabel,networknodelist,newnodeedgelist,isinedge=True):
    # nodelabel is not in networknodelist
    # newnodeedgelist is non-empty list of edge names between nodelabel and the nodes in networknodelist

    (_,othernode,newedgereg) = getRandomEdge(networknodelist)

    tried_edges=set()
    if isinedge:
        inedge = (othernode,nodelabel,newedgereg)       
        while inedge not in newnodeedgelist:
            tried_edges.add(inedge)
            sanityCheckEdgeList(newnodeedgelist,tried_edges)
            (othernode,_,newedgereg) = generateRandomEdge(networknodelist)
            inedge = (othernode,nodelabel,newedgereg)       
    else:
        outedge = (nodelabel,othernode,newedgereg)
        while outedge not in newnodeedgelist:
            tried_edges.add(outedge)
            sanityCheckEdgeList(newnodeedgelist,tried_edges)
            (_,othernode,newedgereg) = generateRandomEdge(networknodelist)
            outedge = (nodelabel,othernode,newedgereg)
    return othernode,newedgereg

def getOrderedEdge(graph_named_edges,edgelist,rank):
    # graph_named_edges (from getNamedEdgesInGraph(graph)) is a list of named adjacencies in the format of edgelist
    # edge list is list of edges to add to network
    numedges = 0
    for (sn,en,rg) in edgelist:
        if not isSignedEdgeInGraph(graph_named_edges,sn,en,rg):
            numedges+=1
        if numedges==rank:
            startnode, endnode, newedgereg = sn, en, rg
            break
    if "startnode" in locals():
        return startnode,endnode,newedgereg
    else:
        raise ValueError("Warning: Too many edges requested. Aborting network creation early.")

def getOrderedNode(networknodelist,nodelist,rank):
    numnodes = 0
    for n in nodelist:
        if n not in networknodelist:
            numnodes+=1
        if numnodes==rank:
            newnode=n
            break
    if "newnode" in locals():
        return newnode
    else:
        raise ValueError("Warning: Too many nodes requested. Aborting network creation early.")

def getRandomNodeFromList(networknodelist,nodelist):
   # sanity check while loop
    sanityCheckNodeList(networknodelist,nodelist)
    n = len(nodelist)
    index = getRandomInt(n)
    while nodelist[index] in networknodelist:
        index = getRandomInt(n)
    return nodelist[index]

def filterEdges(graph_named_edges,nodelabel,networknodelist,edgelist):
    # graph_named_edges (from getNamedEdgesInGraph(graph)) is a list of named adjacencies in the format of edgelist
    # edge list is list of edges to add to network
    inedges=[]
    outedges=[]
    for edge in edgelist:
        if edge not in graph_named_edges:
            if edge[0] in networknodelist and edge[1] == nodelabel:
                inedges.append(edge)
            elif edge[0] == nodelabel and edge[1] in networknodelist:
                outedges.append(edge)
    return inedges,outedges

def addNode(graph,newnodelabel,innode,inreg,outnode,outreg):
    n = len(graph.vertices())
    # the new node will have index n
    graph.add_vertex(n,label=newnodelabel)
    graph.add_edge(innode,n,label=inreg)
    graph.add_edge(n,outnode,label=outreg)
    return graph

def addOrChangeEdge(graph,graph_named_edges,startnode,endnode,newedgereg):
    existing_regulation=isUnsignedEdgeInGraph(graph_named_edges,startnode,endnode)
    if not existing_regulation:
        graph.add_edge(startnode,endnode,label=newedgereg)
    else:
        newedgereg='a'*(existing_regulation == 'r') + 'r'*(existing_regulation == 'a')
        graph.change_edge_label(startnode,endnode,newedgereg)
    return graph

def addRandomEdgeOrRandomEdgeFromList(graph,edgelist=()):
    graph_named_edges = getNamedEdgesInGraph(graph)
    startnode,endnode,newedgereg = getNewRandomEdge(graph_named_edges,edgelist)
    graph = addOrChangeEdge(graph,graph_named_edges,startnode,endnode,newedgereg)
    return graph 

def addRandomEdgesToNewNode(graph,newnodelabel=''):
    networknodelist = getNetworkNodeList(graph)
    # pick outgoing and incoming edges for n from the existing network (i.e. don't pick node n)
    (innode,_,inreg) = generateRandomEdge(networknodelist)
    # pick an outgoing edge for n from the existing network
    (_,outnode,outreg) = generateRandomEdge(networknodelist)
    if not newnodelabel:
        newnodelabel = 'x'+str(len(networknodelist))
    graph = addNode(graph,newnodelabel,innode,inreg,outnode,outreg)
    return graph

def addRandomNodeFromListAndRandomEdgesNoList(graph,nodelist):
    networknodelist = getNetworkNodeList(graph)
    newnodelabel = pickRandomNodeFromList(networknodelist,nodelist)
    graph = addRandomEdgesToNewNode(graph,newnodelabel)
    return graph

def addRandomNodeAndEdgesFromLists(graph,nodelist,edgelist):
    networknodelist = getNetworkNodeList(graph)
    graph_named_edges = getNamedEdgesInGraph(graph)

    def getRandomNodeAndAllowedEdges():
        newnodelabel = getRandomNodeFromList(networknodelist,nodelist)
        inedges,outedges = filterEdges(graph_named_edges,newnodelabel,networknodelist,edgelist)
        return newnodelabel,inedges,outedges

    newnodelabel,inedges,outedges = getRandomNodeAndAllowedEdges()

    # sanity check while loop
    tried_labels=set()
    remaining_labels=set(nodelist).difference(networknodelist)
    while not inedges or not outedges:
        tried_labels.add(newnodelabel)
        if tried_labels == remaining_labels: # if all new nodes have empty edge lists, abort
            raise ValueError("Warning: No appropriate edges in list. Aborting network creation early.")
        newnodelabel,inedges,outedges = getRandomNodeAndAllowedEdges()
    innode,inreg = getRandomInOrOutEdgeFromList(newnodelabel,networknodelist,inedges,isinedge=True)
    outnode,outreg = getRandomInOrOutEdgeFromList(newnodelabel,networknodelist,outedges,isinedge=False)
    graph = addNode(graph,newnodelabel,innode,inreg,outnode,outreg)
    return graph

def addRandomNodeOrderedEdges(graph,nodelist,edgelist,edgerank):
    pass

def addOrderedNodeRandomEdgesNoList(graph,nodelist,noderank):
    pass

def addOrderedNodeRandomEdgesFromList(graph,nodelist,edgelist,noderank):
    pass

def addOrderedNodeOrderedEdges(graph,nodelist,edgelist,noderank,edgerank):
    pass
    

