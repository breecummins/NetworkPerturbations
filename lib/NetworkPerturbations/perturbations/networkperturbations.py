import random, time, itertools, sys
import DSGRN
import NetworkPerturbations.perturbations.graphtranslation as graphtranslation
from functools import partial
from inspect import getmembers, isfunction
import NetworkPerturbations.perturbations.filters as filters

#####################################################################################################################
# Function for perturbing networks.
#####################################################################################################################

def perturbNetwork(params, network_spec):
    '''
    Get a list of essential DSGRN network specifications perturbed around an essential seed network given parameters
    in params (see below). Duplicate networks are possible because there is no graph isomorphism checking.

    :param params: params is a dictionary with the following key,value pairs. Every one has a default,
                   so any of these parameters are optional.
        "nodelist" : a list of node labels (strings) acceptable to add OR None OR empty list
                    default : []
        "edgelist" : a list of ("source","target","regulation") tuples OR None OR empty list
                    default : []
                   NOTE: negative self-loops are removed before perturbation
        "probabilities" : dictionary with operations keying the probability that the operation will occur
                          default: {"addNode" : 0.30, "removeNode" : 0.05, "addEdge" : 0.50, "removeEdge" : 0.15}
                          NOTE: setting any probability to zero will ensure the operation does not occur
                          NOTE: will be normalized if it does not sum to 1
                          NOTE: every added node is also given an inedge and an outedge as part of the operation
        "range_operations" : [int,int] min to max # of node/edge changes allowed per graph, endpoint inclusive
                             default : [1,25]
        "numperturbations" : integer > 0, how many perturbations to construct
                            default: 1000
        "time_to_wait" : number of seconds to wait before halting perturbation procedure (avoid infinite while loop)
                        default : 30
        "maxparams" : integer > 0, parameters per database allowed (eventually this should be deprecated for estimated
                      computation time)
                      default : 100000
        "filters" : default = None, dictionary of filter function name strings from filters.py keying input dictionaries with the needed keyword arguments for each function
                    format: {"function_name1" : kwargs_dict_1, "function_name2" : kwargs_dict_2, ... }
    :param network_spec: DSGRN network specification string
    :return: list of essential DSGRN network specification strings

    '''


    # Initialize
    params, starting_graph = setup(params,network_spec)
    networks = []
    start_time = time.time()

    while (len(networks) < params['numperturbations']) and (time.time()-start_time < params['time_to_wait']):
        # add nodes and edges or just add edges based on params and get the network spec for the new graph
        graph = perform_operations(starting_graph.clone(),params)
        netspec = graphtranslation.createEssentialNetworkSpecFromGraph(graph)
        # check that network spec does not string match another, is small enough, is DSGRN computable,
        # and satisfies user-supplied filters
        # TODO: check for graph isomorphisms, or at least alphabetize netspec for string matching
        if (netspec not in networks) and checkComputability(netspec,params['maxparams']):
            if other_filtering(graph,params,netspec):
                networks.append(netspec)

    # inform user of the number of networks produced and return however many networks were made
    if time.time()-start_time >= params['time_to_wait']:
        print("Process timed out.")
    print("Proceeding with {} networks.".format(len(networks)))
    return networks


##########################################################################################
# Set up functions
##########################################################################################

def setup(params,network_spec):
    # set defaults
    params = set_defaults(params)
    # remove negative self-regulation from edgelist
    if params["edgelist"]:
        params["edgelist"] = filter_edgelist(params["edgelist"])
    # make sure probabilities are normalized and take the cumsum
    params["probabilities"] = make_probability_vector(params["probabilities"])
    # make starting graph, make sure network_spec is essential, and add network_spec to list of networks
    starting_graph = graphtranslation.getGraphFromNetworkSpec(network_spec)
    return params, starting_graph


def set_defaults(params):
    if "nodelist" not in params:
        params["nodelist"] = []
    if "edgelist" not in params:
        params["edgelist"] = []
    if "probabilities" not in params:
        params["probabilities"] = {"addNode" : 0.30, "removeNode" : 0.05, "addEdge" : 0.50, "removeEdge" : 0.15}
    if "range_operations" not in params:
        params["range_operations"] = [1,26]
    else: # add 1 so that endpoint is inclusive
        params["range_operations"] = [params["range_operations"][0],params["range_operations"][1]+1]
    if "numperturbations" not in params:
        params["numperturbations"] = 1000
    if "time_to_wait" not in params:
        params["time_to_wait"] = 30
    if "maxparams" not in params:
        params["maxparams"] = 100000
    if "filters" not in params:
        params["filters"] = None
    else:
        names = list(params["filters"].keys())
        funcs = [o for o in getmembers(filters) if isfunction(o[1]) and o[0] in names]
        not_implemented = set(names).difference([o[0] for o in funcs])
        if not_implemented:
            raise ValueError("\nFilter(s) {} not implemented in filters.py. Please correct the name or add a function.\n".format(not_implemented))
        params["filters"] = [partial(o[1],kwargs=params["filters"][o[0]]) for o in funcs]
    return params


def filter_edgelist(edgelist):
    # filter edgelist to remove negative self-loops
    el = edgelist[:]
    for e in edgelist:
        if e[0] == e[1] and e[2] == "r":
            el.remove(e)
    return el


def make_probability_vector(probabilities):
    probs = [probabilities[k] for k in ["addNode","addEdge","removeEdge","removeNode"]]
    cs =  list(itertools.accumulate(probs))
    return [c/cs[-1] for c in cs]


##########################################################################################
# Check that database is both computable (logic files present) and as small as requested
# and satisfies user-supplied filters
##########################################################################################

def checkComputability(network_spec,maxparams):
    network=DSGRN.Network()
    try:
        network.assign(network_spec)
        paramgraph=DSGRN.ParameterGraph(network) 
        smallenough = paramgraph.size() <= int(maxparams)
        if not smallenough:
            print("\nToo many parameters. Not using network spec: \n{}\n".format(network_spec))
        return smallenough
    except (AttributeError, RuntimeError):
        print("\nNetwork spec not computable: \n{}\n".format(network_spec))
        return False


def other_filtering(graph,params,netspec):
    if params["filters"]:
        for fil in params["filters"]:
            isgood, message = fil(graph)
            if not isgood:
                print("\n" + message + " Not using network spec: \n{}\n".format(netspec))
                return False
    return True


##############################################################################
# Stochastic numbers of additional edges and/or nodes to perturb the network.
##############################################################################


def perform_operations(graph,params):
    # choose the number of each type of operation
    numops = choose_operations(params)
    # apply operations in the proper order
    graph, nodes = addNodes(graph, params["nodelist"],numops[0])
    graph = addConnectingEdges(graph,nodes,params["edgelist"])
    graph = addEdges(graph,params["edgelist"],numops[1])
    graph = removeEdges(graph,numops[2])
    graph = removeNodes(graph,numops[3])
    return graph


def choose_operations(params):
    # choose a random number of graph additions or swaps
    numadds = random.randrange(*params["range_operations"])
    # generate operations with probabilities as given in params
    probs = sorted([random.uniform(0.0, 1.0) for _ in range(numadds)])
    numops=[0,0,0,0]
    for j in range(4):
        p = params["probabilities"][j]
        while probs and probs[0] <= p:
            numops[j]+=1
            probs.pop(0)
    return numops

################################################################################################
# Basic add and remove methods of the network perturbation.
################################################################################################

def removeEdges(graph,numedges):
    for _ in range(numedges):
        graph.remove_edge(*random.choice(graph.edges()))
    return graph

def removeNodes(graph,numnodes):
    for _ in range(numnodes):
        graph.remove_vertex(random.choice(graph.vertices()))
    return graph

def addEdges(graph,edgelist,numedges):
    # if no edgelist, then a random edge is added to the network
    # if edgelist is specified, a random choice is made from the filtered edgelist 
    # (repressing self-loops removed)

    # get info from graph
    networknodenames = getNetworkLabels(graph)
    N = len(networknodenames)
    edges = set([(v, a, graph.edge_label(v, a)) for (v, a) in graph.edges()])
    if edgelist:
        el = list(set([tuple(getVertexFromLabel(graph, e[:2]) + [e[2]]) for e in edgelist if set(e[:2]).issubset(
            networknodenames)]).difference(edges))

    # add edges
    for _ in range(numedges):
        # choose an edge from the list
        if edgelist:
            newedge = getRandomListElement(el)
            if newedge:
                el.remove(newedge)
                graph.add_edge(*newedge)
        # otherwise produce random edge that is not a negative self-loop
        else:
            newedge = None
            if N > 1 or (N == 1 and not edges):
                newedge = getRandomEdge(N)
                while newedge in edges or (newedge[0]==newedge[1] and newedge[2]=='r'):
                    newedge = getRandomEdge(N)
            if newedge:
                edges.append(newedge)
                graph.add_edge(*newedge)
    return graph


def addConnectingEdges(graph,nodes,edgelist):
    # add connecting edges for newly added nodes
    networknodenames = getNetworkLabels(graph)
    N = len(networknodenames)

    for n in nodes:
        # choose an edge from the list
        if edgelist:
            # get in-edge
            el_in = [e for e in edgelist if n == e[1] and e[0] in networknodenames]
            e = getRandomListElement(el_in)
            newinedge = tuple(getVertexFromLabel(graph,e[:2])+[e[2]])
            # get out-edge
            el_out = [e for e in edgelist if n == e[0] and e[1] in networknodenames]
            e = getRandomListElement(el_out)
            newoutedge = tuple(getVertexFromLabel(graph, e[:2]) + [e[2]])
        # otherwise produce random edges that are not negative self-loops
        else:
            # can always add activating self-loop
            newinedge = (getRandomNode(N),n,getRandomReg())
            if newinedge[0] == newinedge[1] and newinedge[2] == 'r':
                newinedge[2] = "a"
            newoutedge = (n,getRandomNode(N), getRandomReg())
            if newoutedge[0] == newoutedge[1] and newoutedge[2] == 'r':
                newoutedge[2] = "a"
        if newinedge:
            graph.add_edge(*newinedge)
        if newoutedge:
            graph.add_edge(*newoutedge)
    return graph


def addNodes(graph,nodelist,numnodes):
    # if nodelist, choose numnodes random nodes from nodelist
    # if no nodelist, make up names for new nodes

    nodes = []
    for _ in range(numnodes):
        networknodenames = getNetworkLabels(graph)
        N = len(networknodenames)

        if not nodelist:
            # make unique node name
            newnodelabel = 'x'+str(N)
            c=1
            while newnodelabel in networknodenames:
                newnodelabel = 'x'+str(N+c)
                c+=1
        else:
            # filter nodelist to get only new nodes
            nl = [ n for n in nodelist if n not in networknodenames ]
            newnodelabel = getRandomListElement(nl)

        # add to graph
        if newnodelabel:
            graph.add_vertex(N,label=newnodelabel)
            nodes.append(newnodelabel)

    return graph, nodes

##################################################################################################
# Helper functions to access graph labels and produce random choices.
##################################################################################################

def getNetworkLabels(graph):
    # need node names to choose new nodes/edges
    return [ graph.vertex_label(v) for v in graph.vertices() ]

def getVertexFromLabel(graph,nodelabels):
    return [ graph.get_vertex_from_label(n) for n in nodelabels ]

def getRandomNode(n):
    # pick node
    return random.randrange(n)

def getRandomEdge(n):
    # pick random edge
    return getRandomNode(n), getRandomNode(n), getRandomReg()

def getRandomReg():
    # pick regulation
    regbool = random.randrange(2)
    return 'a'*regbool + 'r'*(not regbool)

def getRandomListElement(masterlist):
    # pick randomly from list
    if not masterlist: return None
    else: return random.choice(masterlist)

