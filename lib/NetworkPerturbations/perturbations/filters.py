def constrained_inedges(graph,kwargs):
    message = "Wrong number of inedges."
    for u in graph.vertices():
        N = len([v for v in graph.vertices() if u in graph.adjacencies(v)])
        if N < kwargs["min_inedges"] or N > kwargs["max_inedges"]:
            return False, message
    return True, ""
