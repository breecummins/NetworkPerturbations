import pythonmodules.intervalgraph as ig
import itertools,sys

# This code only works if the order of the variables in the reference network spec is repeated in the perturbed network specs (see lines marked (*))
# That is, if the reference network spec has variables A, B, C in order, then the new networks must have an order like A, B, C, x3, x4, ...

def getAllSuggestionGraphs(network_spec,list_of_networks):
    ref_graph = ig.getGraphFromNetworkSpec(network_spec)
    oldnodes = sorted(list(ref_graph.vertices())) # graph.vertices() is a set of integers from 0 to N
    suggestion_graphs = []
    for n in list_of_networks:
        new_graph = ig.getGraphFromNetworkSpec(n) 
        for v in oldnodes: 
            for c in ref_graph.adjacencies(v): new_graph.remove_edge(v,c)  # (*) variable order dependence
        # pick out new nodes that have only a self-loop as an in-edge
        newnodesselfedges = [v for v in new_graph.vertices() if v not in oldnodes and set([v]) == new_graph.transpose().adjacencies(v)] # (*) variable order dependence
        for u in newnodesselfedges: new_graph.remove_edge(u,u) # this avoids some infinite loops in the recursion, increases computation speed, and does not affect the edges we seek
        suggestion_graphs.append(_computeSuggestionGraph(new_graph,oldnodes,newnodesselfedges))
    return ref_graph,suggestion_graphs

def _computeSuggestionGraph(reduced_graph,oldnodes,newnodesselfedges):
    rownodes = oldnodes+newnodesselfedges
    suggestion_graph = ig.Graph()
    for rn in rownodes:
        suggestion_graph.add_vertex(rn)
        terminals = sorted(_condenseEdges([rn],[],oldnodes,reduced_graph))
        for node, regs in itertools.groupby(terminals,lambda x : x[0]):
            regs = [r[1] for r in regs]
            sgn = regs[0] if len(set(regs)) == 1 else 'b'
            suggestion_graph.add_edge(rn,node,label=sgn) # (*) variable order dependence
    return suggestion_graph

def _condenseEdges(path,terminals,oldnodes,graph):
    # recursive
    if len(path) > 1 and path[-1] in oldnodes:
        regs = [graph.edge_label(*p) for p in zip(path[:-1],path[1:])].count('r') # count negative regulations in the path
        sgn = 'r' if regs%2 else 'a'
        terminals.append((path[-1],sgn))
    elif len(path) > 1 and path[-1] not in oldnodes and path.count(path[-1]) > 1:
        pass # break cycles
    else:
        for c in graph.adjacencies(path[-1]):
            _condenseEdges(path+[c],terminals,oldnodes,graph)
    return terminals




