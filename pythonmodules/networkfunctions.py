import random
# graph is an intervalgraph.Graph object

def getRandomInt(n):
    return random.randrange(n)

def isUnsignedEdgeInGraph(graph,startnode,endnode):
    if endnode in graph.adjacencies(startnode):
        return graph.edge_label(startnode,endnode)
    else:
        return False

def isSignedEdgeInGraph(graph,startnode,endnode,newedgereg):
    if ( endnode in graph.adjacencies(startnode) ) and ( graph.edge_label(startnode,endnode) == newedgereg ):
        return True
    else:
        return False        

def isNegSelfLoop(startnode,endnode,newedgereg):
    if startnode==endnode and newedgereg=='r':
        return True
    else:
        return False

def addOrChangeEdge(graph,startnode,endnode,newedgereg):
    existing_regulation=isUnsignedEdgeInGraph(graph,startnode,endnode)
    if not existing_regulation:
        graph.add_edge(startnode,endnode,label=newedgereg)
    else:
        newedgereg='a'*(existing_regulation == 'r') + 'r'*(existing_regulation == 'a')
        graph.change_edge_label(startnode,endnode,newedgereg)
    return graph

def pickRandomEdge(graph,edgelist=()):
    n = len(graph.vertices())
    
    def getRandomEdge():
        startnode = getRandomInt(n)
        endnode = getRandomInt(n)
        regbool = getRandomInt(2)
        newedgereg = 'a'*regbool + 'r'*(not regbool)
    return startnode,endnode,newedgereg

    startnode,endnode,newedgereg = getRandomEdge()    
    if edgelist:         
        while ( endnode == startnode and endnode in graph.adjacencies(startnode) ) or isNegSelfLoop(startnode,endnode,newedgereg) or (startnode,endnode,newedgereg) not in edgelist:
            startnode,endnode,newedgereg = getRandomEdge()
    else:
        while ( endnode == startnode and endnode in graph.adjacencies(startnode) ) or isNegSelfLoop(startnode,endnode,newedgereg):
            startnode,endnode,newedgereg = getRandomEdge()
    return startnode,endnode,newedgereg

def pickOrderedEdge(graph,reg,edgelist,rank):
    numedges = 0
    for (sn,en,rg) in edgelist:
        if not isSignedEdgeInGraph(graph,sn,en,rg):
            numedges+=1
        if numedges==rank:
            startnode, endnode, newedgereg = sn, en, rg
            break
    if "startnode" in locals():
        return startnode,endnode,newedgereg
    else:
        print "Warning: Too many edges requested. Aborting network creation early."
        return False,False,False

def filterEdges(node,edgenamelist,isinedge):
    # if not isinedge, then is out-edge
    sublist=[]
    if isinedge:
        for edge in edgenamelist:
            if edge[1] == node:
                sublist.append(edge)
    else:
        for edge in edgenamelist:
            if edge[0] == node:
                sublist.append(edge)
    return sublist

def convertEdgeListToIndices(networknodelist,edgenamelist):
    edgelist=[]
    for (sn,en,rg) in edgenamelist:
        edgelist.append((networknodelist.index(sn),networknodelist.index(en),rg))
    return edgelist

def addNode(graph,newnodelabel,innode,inreg,outnode,outreg):
    n = len(graph.vertices())
    graph.add_vertex(n,label=newnodelabel)
    graph.add_edge(innode,n,label=inreg)
    graph.add_edge(n,outnode,label=outreg)
    return graph

def pickOrderedNode(networknodelist,nodelist,rank):
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
        print "Warning: Too many nodes requested. Aborting network creation early."
        return False

def pickRandomNodeFromList(networknodelist,nodelist):
    n = len(nodelist)
    if networknodelist == n:
        print "Warning: Too many nodes requested. Aborting network creation early."
        return False        
    index = getRandomInt(n)
    while nodelist[index] in networknodelist:
        index = getRandomInt(n)
    return nodelist[index]

def addRandomEdgeOrRandomEdgeFromList(graph,reg,edgelist=()):
    startnode,endnode,newedgereg = pickRandomEdge(graph,edgelist)
    graph = addOrChangeEdge(graph,startnode,endnode,newedgereg)
    return graph 

def addRandomNodeRandomEdgesNoLists(graph):
    n = len(graph.vertices())
    # the new node will have index n
    # pick an incoming edge for n from the existing network (i.e. don't pick node n)
    innode = getRandomInt(n) # NOT getRandomInt(n+1)
    inbool = getRandomInt(2)
    inreg = 'a'*inbool + 'r'*(not inbool)
    # pick an outgoing edge for n from the existing network
    outnode = getRandomInt(n)
    outbool = getRandomInt(2)
    outreg = 'a'*outbool + 'r'*(not outbool)
    graph = addNode(graph,'x'+str(n),innode,inreg,outnode,outreg)
    return graph

def addRandomNodeFromListAndRandomEdges(graph,reg,nodelist):
    pass

def addOrderedNodeRandomEdges(graph,reg,nodelist,noderank):
    pass

def addRandomNodeAndEdgesFromLists(graph,reg,nodelist,edgenamelist,noderank,edgerank):
    pickOrderedNode(networknodelist,nodelist,rank)

def addOrderedNodeRandomEdgesFromList(graph,reg,nodelist,edgenamelist,noderank):
    pass

def addRandomNodeOrderedEdges(graph,reg,nodelist,edgenamelist,edgerank):
    pass

def addOrderedNodeOrderedEdges(graph,reg,nodelist,edgenamelist,noderank,edgerank):
    pass
    

