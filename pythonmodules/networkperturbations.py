import random, itertools
import DSGRN
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
            graph = perturbNetworkWithNodesAndEdges(graph,params['edgelist'],params['nodelist'],params['maxadditionspergraph'],params['swap_edge_reg'])
        else:
            graph = perturbNetworkWithEdgesOnly(graph,params['edgelist'],params['maxadditionspergraph'],params['swap_edge_reg']) 
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

def perturbNetworkWithNodesAndEdges(graph,edgelist=None,nodelist=None,maxadditions=10,swap_edge_reg=True):
    keepgoing = random.randrange(1,maxadditions+1)
    while keepgoing > 0:
        keepgoing -= 1
        if random.randrange(2):
            graph = addEdge(graph,edgelist,swap_edge_reg)
            if graph is None: break
        else:
            graph = addNodeAndConnectingEdges(graph,edgelist,nodelist)
            if graph is None: break
    return graph

def perturbNetworkWithEdgesOnly(graph,edgelist=None,maxadditions=10,swap_edge_reg=True):
    keepgoing = random.randrange(1,maxadditions+1)
    while keepgoing > 0:
        keepgoing -= 1
        graph = addEdge(graph,edgelist,swap_edge_reg)
        if graph is None: break
    return graph

################################################################################################
# The "add" functions take an intervalgraph.Graph instance and return a modified version of it.
# Basic methods of the network perturbation.
################################################################################################

def addEdge(graph,edgelist=None,swap_edge_reg=True):
    # if no edgelist, then a random edge is added to the network
    # if edgelist is specified, a random choice is made from the filtered edgelist 
    # (existing edges and repressing self-loops removed)
    # if swap_edge_reg, then existing edges in the graph may have their regulation swapped, otherwise existing edges are preserved 

    def isNegSelfLoop(edge):
        if edge[0]==edge[1] and edge[2]=='r': return True
        else: return False

    # get info from graph
    networknodenames = getNetworkLabels(graph)
    N = len(networknodenames)
    graph_edges = [(v,a,graph.edge_label(v,a)) for v in graph.vertices() for a in graph.adjacencies(v)]    
    
    # make a new edge and add it to the graph
    # exclude trivial graphs because no edges can be added or swapped
    if N < 2: newedge = None
    # exclude complete graphs if we can't swap edge regulation because no edges can be added
    elif not swap_edge_reg and all( set(graph.adjacencies(v)) == set(graph.vertices()) for v in graph.vertices() ): newedge = None   
    # choose newedge from filtered edgelist (note that all edges could be filtered out, so that newedge=None is possible)
    # buyer beware -- negative self-loops not removed
    elif edgelist:
        edgelist = [ tuple(getVertexFromLabel(graph,e[:2]).append(e[2])) for e in edgelist if set(e[:2]).issubset(networknodenames) ]
        if swap_edge_reg: edgelist = list(set(edgelist).difference(graph_edges))
        else: edgelist = [ e for e in edgelist if e[1] not in graph.adjacencies(e[0]) ]
        newedge = getRandomListElement(edgelist)
        if newedge is None: graph=None
        else: graph.add_edge(*newedge) 
    # otherwise produce random edge (removing trivial and complete graphs ensures this will succeed)
    # negative self-loops are not added
    else:
        if swap_edge_reg:
            newedge = getRandomEdge(N)
            while newedge in graph_edges or isNegSelfLoop(newedge): newedge = getRandomEdge(N) 
            graph.add_edge(*newedge) 
        else: 
            graph_edges = [ e[:2] for e in graph_edges ]
            nodes = (getRandomNode(N), getRandomNode(N))
            while nodes in graph_edges: nodes = (getRandomNode(N), getRandomNode(N))
            graph.add_edge( nodes[0], nodes[1], getRandomReg() if nodes[0] != nodes[1] else 'a' ) 
    return graph 

def addNodeAndConnectingEdges(graph,edgelist=None,nodelist=None,swap_edge_reg=True):
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
        # get random in and out edges
        # in-edge is allowed to be a self-edge -- imitates drivers in gene networks
        return (getRandomNode(N+1),getRandomReg()), (getRandomNode(N),getRandomReg())

    # get the new node and connecting edges
    if nodelist is None:
        newnodelabel = makeupNode()        
        (innode,inreg),(outnode,outreg) = randomInAndOut()
    else:
        # filter nodelist to get only new nodes
        nodelist = [ n for n in nodelist if n not in networknodenames ]
        if edgelist is None:
            newnodelabel = getRandomListElement(nodelist)
            if newnodelabel is None: graph = None
            else: (innode,inreg),(outnode,outreg) = randomInAndOut()
        else:
            # filter edgelist to get edges to and from network (or self-edges)
            # buyer beware -- negative self-edges not removed
            edgelist = [e for e in edgelist if e[0] in networknodenames or e[1] in networknodenames]
            # with the filtered lists, get a new node and edge
            newnodelabel,inedge,outedge = getNodeAndConnectingEdgesFromLists(nodelist,edgelist)
            if newnodelabel is None: 
                graph = None
            else:
                # transform from node names into node indices to add to graph
                [innode, outnode] = getVertexFromLabel(graph,[inedge[0],outedge[1]]) 
                inreg, outreg = inedge[2], outedge[2]

    # add to graph
    if graph is not None:
        graph.add_vertex(N,label=newnodelabel)
        graph.add_edge(innode,N,label=inreg)
        graph.add_edge(N,outnode,label=outreg)
    return graph

##################################################################################################
# All "get" functions return nodes and/or edges meeting criteria, or throw an error if they can't.
# Helpers for "add" functions.
##################################################################################################

def getNetworkLabels(graph):
    # need node names to choose new nodes/edges
    return [ graph.vertex_label(v) for v in graph.vertices() ]

def getVertexFromLabel(graph,nodelabels):
    return [ graph.get_vertex_from_label(n) for n in nodelabels ]

def getRandomReg():
    # pick regulation
    regbool = random.randrange(2)
    return 'a'*regbool + 'r'*(not regbool)

def getRandomNode(n):
    # pick node
    return random.randrange(n)

def getRandomEdge(n):
    # pick random edge
    return (getRandomNode(n),getRandomNode(n),getRandomReg())

def getRandomListElement(masterlist):
    # pick randomly from list
    if not masterlist: return None
    else: return masterlist[random.randrange(len(masterlist))]

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
        if nodelabel is None: break
        nodelist.remove(nodelabel)
        nodelabel,inedge,outedge = generateCandidate()
    return nodelabel,inedge,outedge
