import random

def getRandomInt(n):
    return random.randrange(n)

def isUnsignedEdgeInGraph(graph,reg,startnode,endnode):
    if endnode in graph[startnode]:
        ind = graph[startnode].index(endnode)
        return reg[startnode][ind]
    else:
        return False

def isSignedEdgeInGraph(graph,reg,startnode,endnode,newedgereg):
    if ( endnode in graph[startnode] ) and ( reg[startnode][graph[startnode].index(endnode)] == newedgereg ):
        return True
    else:
        return False        

def isNegSelfLoop(startnode,endnode,newedgereg):
    if startnode==endnode and newedgereg=='r':
        return True
    else:
        return False

def addOrChangeEdge(graph,reg,startnode,endnode,newedgereg):
    existing_regulation=isUnsignedEdgeInGraph(graph,reg,startnode,endnode)
    if not existing_regulation:
        graph,reg=addNewEdge(graph,reg,startnode,endnode,newedgereg)
    else:
        reg=changeEdgeRegulation(graph,reg,startnode,endnode,existing_regulation)
    return graph, reg

def addNewEdge(graph,reg,startnode,endnode,newedgereg):
    graph[startnode].append(endnode)
    reg[startnode].append(newedgereg)
    return graph,reg

def changeEdgeRegulation(graph,reg,startnode,endnode,existing_regulation):
    ind = graph[startnode].index(endnode)
    reg[startnode][ind] = 'a'*(existing_regulation == 'r') + 'r'*(existing_regulation == 'a')
    return reg

def pickRandomEdge(graph,reg,edgelist=()):
    n = len(graph)
    
    def getRandomEdge():
        startnode = getRandomInt(n)
        endnode = getRandomInt(n)
        regbool = getRandomInt(2)
        newedgereg = 'a'*regbool + 'r'*(not regbool)
    return startnode,endnode,newedgereg

    startnode,endnode,newedgereg = getRandomEdge()    
    if edgelist:         
        while ( endnode == startnode and endnode in graph[startnode] ) or isNegSelfLoop(startnode,endnode,newedgereg) or (startnode,endnode,newedgereg) not in edgelist:
            startnode,endnode,newedgereg = getRandomEdge()
    else:
        while ( endnode == startnode and endnode in graph[startnode] ) or isNegSelfLoop(startnode,endnode,newedgereg):
            startnode,endnode,newedgereg = getRandomEdge()
    return startnode,endnode,newedgereg

def pickOrderedEdge(graph,reg,edgelist,rank):
    numedges = 0
    for (sn,en,rg) in edgelist:
        if not isSignedEdgeInGraph(graph,reg,sn,en,rg):
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

def addNode(graph,reg,innode,inreg,outnode,outreg):
    graph[innode].append(len(graph))
    reg[innode].append(inreg)
    graph.append([outnode])
    reg.append([outreg])
    return graph,reg

def addRandomNodeRandomEdges(graph,reg):
    n = len(graph)
    # the new node will have index n
    # pick an incoming edge for n from the existing network (i.e. don't pick node n)
    innode = getRandomInt(n) # NOT getRandomInt(n+1)
    inreg = getRandomInt(2)
    graph[innode].append(n)
    reg[innode].append('a'*inreg + 'r'*(not inreg))
    # pick an outgoing edge for n from the existing network
    outnode = getRandomInt(n)
    outreg = getRandomInt(2)
    graph.append([outnode])
    reg.append(['a'*outreg + 'r'*(not outreg)])
    return graph, reg

def addRandomNodeRandomEdgesFromList(graph,reg,nodelist,edgenamelist):
    pass

def addOrderedNodeRandomEdges(graph,reg,nodelist,rank):
    pass

def addRandomNodeOrderedEdges(graph,reg,edgenamelist):
    pass

def addOrderedNodeOrderedEdges(graph,reg,nodelist,edgenamelist,noderank,edgerank):
    pass
    

