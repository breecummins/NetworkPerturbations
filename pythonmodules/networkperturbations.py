import networkfunctions
from databasecomputability import checkComputability
import random
import intervalgraph
import signal, os
import DSGRN


##############################################################################
# Check that database is both computable and as small as requested
##############################################################################

def checkComputability(network_spec,maxparams):
    network=DSGRN.Network()
    network.assign(network_spec)
    try:
        paramgraph=DSGRN.ParameterGraph(network)    
        return (paramgraph.size() <= int(maxparams))
    except:
        return False

##########################################################################################
# set up handler to interrupt network perturbations if it is taking too long to generate
##########################################################################################

def handler(signum, frame):
    print "Network perturbation generation timed out. Proceeding with fewer than desired perturbations."
    raise RuntimeError()

##############################################################################
# Helper functions for network perturbation.
##############################################################################

def perturbNetworkWithNodesAndEdges(graph,edgelist=(),nodelist=()):
    keepgoing = 1
    while keepgoing:
        edge = random.randrange(2)
        if edge:
            graph = networkfunctions.addEdge(graph,edgelist)
        else:
            graph = networkfunctions.addNodeAndConnectingEdges(graph,nodelist,edgelist)
        keepgoing = random.randrange(2)
    return graph

def perturbNetworkWithEdgesOnly(graph,edgelist=()):
    keepgoing = 1
    while keepgoing:
        graph = networkfunctions.addEdge(graph,edgelist)
        keepgoing = random.randrange(2)
    return graph

#################################################################################################
# Perturbations: any number of nodes/edges may be added, but will be filtered via computability.
#################################################################################################

def perturbNetwork(network_spec,maxparams,numperturbations,edgelist=(),nodelist=(),add_madeup_nodes='n',time_to_wait=300):
    # reset random seed for every run
    random.seed()

    # make starting graph, make sure network_spec is essential, add network_spec to list of networks
    starting_graph = intervalgraph.getGraphFromNetworkSpec(network_spec)
    network_spec = intervalgraph.createEssentialNetworkSpecFromGraph(starting_graph)
    networks = [network_spec]

    # Set a signal handler with a time-out alarm
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(time_to_wait)

    # now make perturbations
    # note that the while loop below can be an infinite loop if numperturbations is too large for maxparams
    # that is why there is a signal time-out
    try:
        while len(networks) < int(numperturbations)+1: 
            # explicitly copy or else the starting graph gets reassigned within perturbNetwork functions
            graph = starting_graph.clone()
            if nodelist or add_madeup_nodes == 'y':
                graph = networkfunctions.perturbNetworkWithNodesAndEdges(graph,edgelist,nodelist) # add nodes and edges
            else:
                graph = networkfunctions.perturbNetworkWithEdgesOnly(graph,edgelist) # add just edges
            # get the perturbed network spec
            new_network_spec = intervalgraph.createEssentialNetworkSpecFromGraph(graph)

            # TODO: check for graph isomorphisms in added nodes (only have string matching below). 
            # Can get nodes added in different orders with same edges. Should be rare in general, so not high priority.

            # check that network spec is all of unique, small enough, and computable, then add to list
            if (network_spec not in networks) and checkComputability(network_spec,maxparams):
                networks.append(network_spec)
        signal.alarm(0) # Disable the alarm when the while loop completes
        return networks
    except:
        # return however many networks were made before the time-out
        signal.alarm(0) # Disable the alarm after it triggers
        return networks