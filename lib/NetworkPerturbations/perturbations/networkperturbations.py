import random, time, itertools
from functools import partial
import DSGRN
import NetworkPerturbations.perturbations.graphtranslation as graphtranslation
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
        "range_operations" : [int,int] min to max # of node/edge changes allowed per graph, endpoint inclusive
                             default : [1,25]
        "numperturbations" : integer > 0, how many perturbations to construct
                            default: 1000
        "time_to_wait" : number of seconds to wait before halting perturbation procedure (avoid infinite while loop)
                        default : 30
        "maxparams" : integer > 0, parameters per database allowed (eventually this should be deprecated for estimated
                      computation time)
                      default : 100000
        "filters" : default = None, not yet implemented, list of filter functions to be satisfied
    :param network_spec: DSGRN network specification string
    :return: list of essential DSGRN network specification strings

    '''

    params, starting_graph = setup(params,network_spec)
    # print(graphtranslation.createEssentialNetworkSpecFromGraph(starting_graph))

    # Set a timer for the while loop, which can be infinite if numperturbations is too large for maxparams
    start_time = time.time()
    current_time = 0.0
    networks = []

    while (len(networks) < params['numperturbations']) and (current_time < params['time_to_wait']):
        # choose a random number of graph additions or swaps
        numadds = random.randrange(*params["range_operations"])
        # add nodes and edges or just add edges based on params
        # explicitly copy so that original graph is unchanged
        graph = choose_operations(starting_graph.clone(),params,numadds)
         # get the perturbed network spec
        netspec = graphtranslation.createEssentialNetworkSpecFromGraph(graph)

        # TODO: check for graph isomorphisms in added nodes (only have string matching below). Can get nodes
        #  added in different orders with same edges.

        # TODO: Implement filters (e.g. is_connected, is_feed_forward, constrained_inedges, ...)

        # check that network spec does not string match another, is small enough, is DSGRN computable,
        # and satisfies user-supplied filters
        if (netspec not in networks) and checkComputability(netspec,params['maxparams']):
            isgood = True
            if params["filters"]:
                for fil in params["filters"]:
                    for f,kwargs in fil.items():
                        g = eval("filters."+f)
                        isgood, message = g(graph, kwargs)
                        if not isgood:
                            print(message + " Not using network spec: \n{}\n".format(network_spec))
                            break
            if isgood:
                networks.append(netspec)
        current_time = time.time()-start_time

    # inform user of the number of networks produced
    if current_time >= params['time_to_wait']:
        print("Process timed out.")
    print("Proceeding with {} networks.".format(len(networks)))
    # Return however many networks were made
    return networks


##########################################################################################
# Set up functions
##########################################################################################

def setup(params,network_spec):
    # set defaults
    params = set_defaults(params)
    # remove negative self-regulation from edgelist
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
    return params


def filter_edgelist(edgelist):
    # filter edgelist to remove negative self-loops
    el = edgelist[:]
    for e in edgelist:
        if e[0] == e[1] and e[2] == "r":
            el.remove(e)
    return el


def make_probability_vector(probabilities):
    probs = [probabilities[k] for k in ["addNode","removeNode","addEdge","removeEdge"]]
    cs =  list(itertools.accumulate(probs))
    return [c/cs[-1] for c in cs]


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
            print("\nToo many parameters. Not using network spec: \n {}\n".format(network_spec))
        return smallenough
    except (AttributeError, RuntimeError):
        print("\nNetwork spec not computable: \n{}\n".format(network_spec))
        return False

##############################################################################
# Stochastic numbers of additional edges and/or nodes to perturb the network.
##############################################################################

def choose_operations(graph,params,numadds):
    probs = params["probabilities"]
    while numadds > 0:
        numadds -= 1
        p = random.uniform(0.0, 1.0)
        if p <= probs[0]:
            graph = addNode(graph,params["nodelist"])
        elif p <= probs[1]:
            graph = removeNode(graph)
        elif p <= probs[2]:
            graph = addEdge(graph,params["edgelist"])
        else:
            graph = removeEdge(graph)
    return graph


################################################################################################
# Basic add and remove methods of the network perturbation.
################################################################################################

def removeEdge(graph):
    graph.remove_edge(*random.choice(graph.edges()))
    return graph

def removeNode(graph):
    graph.remove_vertex(random.choice(graph.vertices()))
    return graph

def addEdge(graph,edgelist):
    # if no edgelist, then a random edge is added to the network
    # if edgelist is specified, a random choice is made from the filtered edgelist 
    # (repressing self-loops removed)

    # get info from graph
    networknodenames = getNetworkLabels(graph)
    N = len(networknodenames)
    graph_edges = [(v, a, graph.edge_label(v, a)) for v in graph.vertices() for a in graph.adjacencies(v)]

    # choose an edge from the list
    if edgelist:
        el = [ tuple(getVertexFromLabel(graph,e[:2])+[e[2]]) for e in edgelist if set(e[:2]).issubset(networknodenames) ]
        el = list(set(el).difference(graph_edges))
        newedge = getRandomListElement(el)
    # otherwise produce random edge that is not a negative self-loop
    else:
        newedge = None
        if N > 1 or (N == 1 and not graph_edges):
            newedge = getRandomEdge(N)
            while newedge in graph_edges or (newedge[0]==newedge[1] and newedge[2]=='r'):
                newedge = getRandomEdge(N)
    if newedge:
        graph.add_edge(*newedge)
    return graph


def addNode(graph,nodelist,edgelist):
    # if nodelist, choose random node from nodelist
    # if no nodelist, make up a name for a new node

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

    return graph

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

