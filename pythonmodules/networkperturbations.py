import random
import DSGRN
from operator import xor
import intervalgraph
import time

#####################################################################################################################
# Library for perturbing networks. The method perturbNetworks is expected to be the only externally called function.
#####################################################################################################################

def perturbNetwork(params):
    # params is a dictionary with the following key,value pairs: 
    # network_spec : DSGRN format json string
    # edgelist : a list of ("source","target","regulation") tuples OR None OR empty list
    # nodelist : a list of node labels (strings) acceptable to add OR None OR empty list
    # numperturbations : integer > 0; how many perturbations to construct
    # time_to_wait : number of seconds to wait before halting perturbation procedure (avoid infinite while loop)
    # add_madeup_nodes :  'y' or 'n'; add anonymous nodes to network (no nodelist supplied, but want nodes added)
    # maxparams : integer > 0; parameters per database are allowed (eventually this should be deprecated for estimated db time calculation)
    # maxiterations : integer > 0; how many times can a single perturbation be added to a network (failures are possible, overestimate)

    # reset random seed for every run
    random.seed()

    # make starting graph, make sure network_spec is essential, and add network_spec to list of networks
    starting_graph = intervalgraph.getGraphFromNetworkSpec(params['network_spec'])
    network_spec = intervalgraph.createEssentialNetworkSpecFromGraph(starting_graph)
    networks = [network_spec]

    # Set a timer for the while loop, which can be infinite if numperturbations is too large for maxparams
    start_time = time.time()
    current_time = time.time()-start_time

    # now make perturbations
    while (len(networks) < params['numperturbations']+1) and (current_time < params['time_to_wait']): 
        # explicitly copy so that original graph is unchanged
        graph = starting_graph.clone()
        # add nodes and edges or just add edges based on params
        # this can fail, in which case None is returned
        if params['nodelist'] or (not params['edgelist'] and params['add_madeup_nodes'] == 'y'):
            graph = perturbNetworkWithNodesAndEdges(graph,params['edgelist'],params['nodelist'],params['maxiterations'])
        else:
            graph = perturbNetworkWithEdgesOnly(graph,params['edgelist'],params['maxiterations']) 
        if graph is not None:
            # get the perturbed network spec
            network_spec = intervalgraph.createEssentialNetworkSpecFromGraph(graph)

            # TODO: check for graph isomorphisms in added nodes (only have string matching below). 
            # Can get nodes added in different orders with same edges. Should be rare in general, so not high priority.
            # BUT it might be more common than you'd think, since we filter given a maximum number of parameters.

            # check that network spec is all of unique (in string match, not isomorphism), small enough, and computable, then add to list
            if (network_spec not in networks) and checkComputability(network_spec,params['maxparams']):
                networks.append(network_spec)
        current_time = time.time()-start_time
    if current_time > params['time_to_wait']:
        print "Network perturbation timed out. Proceeding with fewer than requested perturbations."
    # Return however many networks were made
    return networks


##########################################################################################
# Check that database is both computable (logic files present) and as small as requested
##########################################################################################

def checkComputability(network_spec,maxparams):
    network=DSGRN.Network()
    try:
        network.assign(network_spec)
        paramgraph=DSGRN.ParameterGraph(network) 
        smallenough = paramgraph.size() <= int(maxparams)
        if not smallenough:
            print "\nToo many parameters. Not using network spec: \n {}\n".format(network_spec)    
        return smallenough
    except (AttributeError, RuntimeError):
        print "\nNetwork spec not computable: \n{}\n".format(network_spec)
        return False

##############################################################################
# Stochastic numbers of additional edges and/or nodes to perturb the network.
##############################################################################

def perturbNetworkWithNodesAndEdges(graph,edgelist=None,nodelist=None,maxiterations=10**4):
    count = 0
    keepgoing = 1
    while keepgoing and count < maxiterations:
        count += 1
        if random.randrange(2):
            graph = addEdge(graph,edgelist)
            if graph is None:
                return None
        else:
            graph = addNodeAndConnectingEdges(graph,edgelist,nodelist)
            if graph is None:
                return None
        keepgoing = random.randrange(2)
    return graph

def perturbNetworkWithEdgesOnly(graph,edgelist=None,maxiterations=10**4):
    count = 0
    keepgoing = 1
    while keepgoing and count < maxiterations:
        count += 1            
        graph = addEdge(graph,edgelist)
        if graph is None:
            return None
        keepgoing = random.randrange(2)
    return graph

################################################################################################
# The "add" functions take an intervalgraph.Graph instance and return a modified version of it.
# Basic methods of the network perturbation.
################################################################################################

def addEdge(graph,edgelist=None):
    # if no edgelist, then a random edge is added to the network
    # if edgelist is specified, a random choice is made from the filtered edgelist 
    # (existing edges and repressing self-loops removed)

    def isNegSelfLoop(edge):
        if edge[0]==edge[1] and edge[2]=='r':
            return True
        else:
            return False

    # exclude trivial graphs
    networknodenames = getNetworkLabels(graph)
    if len(networknodenames) < 2: 
        return None  

    # transform graph into a list of edge tuples using vertex labels instead of vertex indices
    graph_named_edges = [(graph.vertex_label(v),graph.vertex_label(a),graph.edge_label(v,a)) for v in graph.vertices() for a in graph.adjacencies(v)] 

    # get a new edge
    if edgelist:
        # filter given edgelist to return only edges that can be added to the existing network
        edgelist = [e for e in edgelist if e[0] in networknodenames and e[1] in networknodenames and e not in graph_named_edges and not isNegSelfLoop(e)]
        newedge = getRandomListElement(edgelist)
        if newedge is None:
            return None
    else:
        newedge = getRandomEdge(networknodenames)  
        while newedge in graph_named_edges or isNegSelfLoop(newedge):
            # will terminate for nontrivial (n>1) graphs, because not all possible edges can exist simultaneously in a nontrivial network
            newedge = getRandomEdge(networknodenames)  

    # add the new edge to the graph
    [startnode,endnode] = getVertexFromLabel(graph,newedge[:2]) 
    if endnode in graph.adjacencies(startnode):
        graph.change_edge_label(startnode,endnode,newedge[2])
    else:
        graph.add_edge(startnode,endnode,label=newedge[2])
    return graph 

def addNodeAndConnectingEdges(graph,edgelist=None,nodelist=None):
    # choose new node and connecting edges
    # if nodelist, choose random node from a (filtered) list
    #   if edgelist, choose random in- and out-edges from a (filtered) list
    #   if no edgelist, choose in- and out-edges randomly without a list
    # if no nodelist, make up a name for a new node (and add random edges sans edgelist)

    networknodenames = getNetworkLabels(graph)
    N = len(networknodenames)

    def makeupNode():
        # make unique node name
        newnodelabel = 'x'+str(N)
        c=1
        while newnodelabel in networknodenames:
            # must terminate because networknodenames is finite
            newnodelabel = 'x'+str(N+c)
            c+=1
        return newnodelabel

    def randomInAndOut():
        return getRandomHalfEdge(N), getRandomHalfEdge(N)

    # get the new node and connecting edges
    if nodelist is None:
        newnodelabel = makeupNode()        
        (innode,inreg),(outnode,outreg) = randomInAndOut()
    else:
        # filter nodelist to get only new nodes
        nodelist = [ n for n in nodelist if n not in networknodenames ]
        if edgelist is None:
            newnodelabel = getRandomListElement(nodelist)
            if newnodelabel is None:
                return None
            (innode,inreg),(outnode,outreg) = randomInAndOut()
        else:
            # filter edgelist to get only edges to and from network
            edgelist = [e for e in edgelist if xor(e[0] in networknodenames,e[1] in networknodenames)]
            # with the filtered lists, get a new node and edge
            newnodelabel,inedge,outedge = getNodeAndConnectingEdgesFromLists(nodelist,edgelist)
            if newnodelabel is None or inedge is None or outedge is None:
                return None
            # transform from node names into node indices to add to graph
            [innode, outnode] = getVertexFromLabel(graph,[inedge[0],outedge[1]]) 
            inreg, outreg = inedge[2], outedge[2]

    # add to graph
    graph.add_vertex(N,label=newnodelabel)
    graph.add_edge(innode,N,label=inreg)
    graph.add_edge(N,outnode,label=outreg)
    return graph

##############################################################################
# Low level functions for managing network nodes.
# Helpers for "add" functions.
##############################################################################

def getNetworkLabels(graph):
    # need node names to choose new nodes/edges
    return [ graph.vertex_label(v) for v in graph.vertices() ]

def getVertexFromLabel(graph,nodelabels):
    return [ graph.get_vertex_from_label(n) for n in nodelabels ]


##################################################################################################
# All "get" functions return nodes and/or edges meeting criteria, or throw an error if they can't.
# Helpers for "add" functions.
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

def getRandomListElement(masterlist):
    # masterlist = (filtered) nodelist or edgelist (e.g. get rid of existing network objects, restrict to subset of nodes, ignore negative self-loops)
    # pick randomly from list
    if not masterlist:
        return None
    else:
        return masterlist[random.randrange(len(masterlist))]

def getNodeAndConnectingEdgesFromLists(nodelist,edgelist):
    # nodelist has only NEW nodes and edgelist has only in- and out-edges to and from the EXISTING network 
    # (i.e. both lists are pre-filtered)

    def generateCandidate():
        # randomly pick new node (will return None when nodelist is empty)
        nodelabel = getRandomListElement(nodelist)
        # filter edgelist to find all incoming and outgoing edges to and from nodelabel
        inedges,outedges=[],[]
        for e in edgelist:
            if e[0] == nodelabel: outedges.append(e)
            elif e[1] == nodelabel: inedges.append(e)
        # pick random in and out edges provided they exist, else return None
        return nodelabel, getRandomListElement(inedges), getRandomListElement(outedges)

    nodelabel,inedge,outedge = generateCandidate()
    while inedge is None or outedge is None:
        if nodelabel is None: 
            return None, None, None
        nodelist.remove(nodelabel)
        nodelabel,inedge,outedge = generateCandidate()
    return nodelabel,inedge,outedge
