import networkx as nx


def constrained_inedges(graph,kwargs):
    # kwargs = { "min_inedges" : integer, "max_inedges" : integer }
    # return bool (True if satisfied) and string containing error message
    for u in graph.vertices():
        N = len([v for v in graph.vertices() if u in graph.adjacencies(v)])
        if N < kwargs["min_inedges"] or N > kwargs["max_inedges"]:
            return False, "Number of in-edges not in range."
    return True, ""


def is_feed_forward(graph,kwargs):
    # kwargs = {}, here only for API compliance
    # return bool (True if satisfied) and string containing error message
    G = nx.DiGraph()
    G.add_edges_from(graph.edges())
    scc = nx.strongly_connected_components(G)
    # throw out graphs with non-trivial cycles
    if any(len(s) > 1 for s in scc):
        return False, "Contains cycles."
    return True, ""
