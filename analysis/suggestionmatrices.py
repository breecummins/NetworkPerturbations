import pythonmodules.intervalgraph as ig
import numpy as np
import itertools,json

# This code only works if the order of the variables in the reference network spec is repeated in the perturbed network specs.
# That is, if the reference network spec has variables A, B, C in order, then the new network must have an order like A, B, C, x3, x4, ...

def getNetworkGraph(network_spec,isfile=True):
    if isfile:
        with open(network_spec,'r') as f: 
            graph = ig.getGraphFromNetworkSpec(f.read())
    else: graph = ig.getGraphFromNetworkSpec(network_spec)
    return graph

def computeRefMatrix(ref_graph):
    vertices = graph.vertices()
    ref_matrix = np.zeros(len(vertices),len(vertices))
    for v in vertices:
        for c in graph.adjacencies(v):
            reg = graph.edge_label(v,c)
            ref_matrix[vertices.index(v)][vertices.index(c)] = 1 if reg == 'a' else -1
    return ref_matrix 

def dropOldEdges(ref_graph,new_graph):
    for v in ref_graph.vertices():
        for c in ref_graph.adjacencies(v):
            new_graph.remove_edge(v,c)

def computeSuggestionMatrix(reduced_graph,oldnodes,newnodesselfedges):
    rownodes = oldnodes+newnodesselfedges
    suggestion_matrix = np.zeros(len(rownodes),len(oldnodes))
    for on in rownodes:
        signs = sorted(condenseEdges([on],[],oldnodes,reduced_graph))
        for node, regs in itertools.groupby(signs,lambda x : x[0]):
            num = len(set(regs)) if 'a' in regs else -1
            suggestion_matrix[rownodes.index(on)][oldnodes.index(node)] = num
    return suggestion_matrix

def condenseEdges(path,signs,oldnodes,graph):
    # recursive
    if path[-1] in oldnodes and len(path) > 1:
        regs = [graph.edge_label(*p) for p in zip(path[:-1],path[1:])].count('r') # count negative regulations in the path
        sgn = 'r' if regs%2 else 'a'
        signs.append((path[-1],sgn))
    else:
        for c in graph.adjacencies(path[-1]):
            condenseEdges(path+[c],signs,oldnodes,graph)
    return signs

def getAllMatrices(reference_network_file,perturbation_json_file):
    ref_graph = getNetworkGraph(reference_network_file,isfile=True)
    oldnodes = range(len(ref_graph.vertices()))
    ref_matrix = computeRefMatrix(ref_graph)
    with open(perturbation_json_file,'r') as f:
        list_of_networks = json.load(f)
    suggestion_matrices = []
    for n in list_of_networks:
        new_graph = getNetworkGraph(n,isfile=False)
        reduced_graph = dropOldEdges(ref_graph,new_graph)
        newnodesselfedges = [v for v in reduced_graph.vertices() if v not in oldnodes and v in reduced_graph.adjacencies(v)]
        suggestion_matrices.append(computeSuggestionMatrix(reduced_graph,oldnodes,newnodesselfedges))
    return list_of_networks, suggestion_matrices




