import DSGRN

def hasCycleMatchInStableFC(events,event_ordering,networkspec):
    network = DSGRN.Network(networkspec)
    poe = DSGRN.PosetOfExtrema(network,events,event_ordering)
    patterngraph = DSGRN.PatternGraph(poe)
    paramgraph = DSGRN.ParameterGraph(network)
    for paramind in range(paramgraph.size()):
        domaingraph = DSGRN.DomainGraph(paramgraph.parameter(paramind))
        morsedecomposition = DSGRN.MorseDecomposition(domaingraph.digraph())
        morsegraph = DSGRN.MorseGraph(domaingraph,morsedecomposition)
        for i in range(0,morsedecomposition.poset().size()):
             if morsegraph.annotation(i)[0] == "FC" and len(morsedecomposition.poset().children(i)) == 0:
                searchgraph = DSGRN.SearchGraph(domaingraph,i)
                matchinggraph = DSGRN.MatchingGraph(searchgraph,patterngraph)
                if DSGRN.CycleMatch(matchinggraph):
                    return True
                else:
                    continue
    return False

def hasCycleMatch(events,event_ordering,networkspec):
    network = DSGRN.Network(networkspec)
    poe = DSGRN.PosetOfExtrema(network,events,event_ordering)
    patterngraph = DSGRN.PatternGraph(poe)
    paramgraph = DSGRN.ParameterGraph(network)
    for paramind in range(paramgraph.size()):
        domaingraph = DSGRN.DomainGraph(paramgraph.parameter(paramind))
        searchgraph = DSGRN.SearchGraph(domaingraph)
        matchinggraph = DSGRN.MatchingGraph(searchgraph, patterngraph)
        if DSGRN.CycleMatch(matchinggraph):
            return True
    return False

def hasPathMatch(events, event_ordering, networkspec):
    network = DSGRN.Network()
    network.assign(networkspec)
    poe = DSGRN.PosetOfExtrema(network, events, event_ordering)
    patterngraph = DSGRN.PatternGraph(poe)
    paramgraph = DSGRN.ParameterGraph(network)
    for paramind in range(paramgraph.size()):
        domaingraph = DSGRN.DomainGraph(paramgraph.parameter(paramind))
        morsedecomposition = DSGRN.MorseDecomposition(domaingraph.digraph())
        morsegraph = DSGRN.MorseGraph()
        morsegraph.assign(domaingraph, morsedecomposition)
        for i in range(0, morsedecomposition.poset().size()):
            ms = morsedecomposition.morseset(i)
            if morsegraph.annotation(i)[0] == "FC" and len(morsedecomposition.poset().children(i)) == 0:
                searchgraph = DSGRN.SearchGraph(domaingraph, i)
                matchinggraph = DSGRN.MatchingGraph(searchgraph, patterngraph)
                if DSGRN.QueryCycleMatch(matchinggraph):
                    return True
                else:
                    continue
    return False

def createPosetFromData(timeseries):
    pass

if __name__== "__main__":
    networkspec="X : X + Y \n" + "Y : ~X \n"
    events = [("X", "min"), ("Y", "min"), ("X", "max"), ("Y", "max")]
    event_ordering = [(0, 2), (1, 3)]
    print(hasCycleMatchInStableFC(events,event_ordering,networkspec))
