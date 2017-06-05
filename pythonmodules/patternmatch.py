import DSGRN

def makePattern(poset,events,final_label,dim):
	return DSGRN.Pattern.Pattern(poset,events,final_label,dim)

def queryOnFC(pattern,domaingraph,morseset_index):
    patterngraph = DSGRN.Pattern.PatternGraph(pattern)
    searchgraph = DSGRN.Pattern.SearchGraph(domaingraph,morseset_index)
    matchinggraph = DSGRN.Pattern.MatchingGraph(searchgraph,patterngraph)
    return DSGRN.Pattern.PatternMatch.QueryCycleMatch(matchinggraph)

def searchForPattern(pattern,networkfile=None,networkspec=None):
    if networkfile:
        network = DSGRN.Network(networkfile)
    elif networkspec:
        network = DSGRN.Network()
        network.assign(networkspec)
    else:
        raise ValueError("No input network.")
    names = [network.name(i) for i in range(network.size())]
    paramgraph = DSGRN.ParameterGraph(network)
    for paramind in range(paramgraph.size()):
        domaingraph = DSGRN.DomainGraph(paramgraph.parameter(paramind))
        morsedecomposition = DSGRN.MorseDecomposition(domaingraph.digraph())
        poset = morsedecomposition.poset()
        for i in range(0,morsedecomposition.poset().size()):
            ms = morsedecomposition.morseset(i)
            if len(ms) > 1 and morsegraph.annotation(i)[0] == "FC" and len(poset.children(i)) == 0:
                if queryOnFC(pattern,domaingraph,i):
                    return True
                else:
                    continue
    return False

def main():
    pass
