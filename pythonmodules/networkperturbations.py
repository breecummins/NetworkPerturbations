import networkfunctions

# The purpose of these functions must be to parse and filter node and edge lists. Then the function calls
# should be identical: perturbNetwork wrapped in a computability and uniqueness checker.

#######################################################################################################################
# Need total number of perturbations. Any number of nodes/edges may be added, but will be filtered via computability.
#######################################################################################################################

def randomEdges(network_spec,maxparams,numperturbations):
    pass

def randomNodeRandomEdges(network_spec,maxparams,numperturbations):
    pass

def randomEdgesFromList(network_spec,maxparams,numperturbations,edgelist):
    pass

def randomNodeFromListRandomEdges(network_spec,maxparams,numperturbations,nodelist):
    pass

def randomNodeFromListRandomEdgesFromList(network_spec,maxparams,numperturbations,nodelist,edgelist):
    pass

#######################################################################################################################
# Need number of distinct nodes and number of edge sets to add to each node. Filtered via computability.
#######################################################################################################################

def randomNodeFromListOrderedEdgesFromList(network_spec,maxparams,nodelist,numnodes,maxnumedgesets,edgelist):
    pass

def orderedNodeFromListRandomEdges(network_spec,maxparams,nodelist,numnodes,maxnumedgesets):
    pass

def orderedNodeFromListRandomEdgesFromList(network_spec,maxparams,nodelist,numnodes,maxnumedgesets,edgelist):
    pass

#######################################################################################################################
# Need number of distinct nodes/edges and number of simultaneous additions allowed. Will be computed deterministically 
# and filtered via computability.
#######################################################################################################################

def orderedEdgesFromList(network_spec,maxparams,edgelist,numedges,simultaneous):
    pass

def orderedNodeFromListOrderedEdgesFromList(network_spec,maxparams,nodelist,numnodes,edgelist,numedges,simultaneous):
    pass