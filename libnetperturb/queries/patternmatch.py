import DSGRN
import sys, json, os, ast
sys.path.append('../../min_interval_posets')
from min_interval_posets import libposets
from libnetperturb.perturbations import fileparsers

def query(networks,resultsdir,params):
    '''
    For each epsilon in a list of epsilons, a poset from time series data is created. This poset is matched against the
    domain graph for each parameter in each network from a list of networks. The result is True if there is at least one
    match, False if not, or a count of the number of parameters with a match.

    :param networks: list of network specification strings in DSGRN format
    :param resultsdir: path to directory where results file(s) will be stored
    :param params: A dictionary containing the keys
        "epsilons" : list of floats 0 <= x <= 1, one poset will be made for each x
        "matchingfunction" : a string containing the name of one of the matching functions in this module
        "count" : True or False, whether to count all params or shortcut at first success
        Then, one can either specify posets directly, or extract posets from timeseries data.
        Include either
        "posets" : list of tuples of epsilon with a DSGRN formatted poset:
                    [(eps1,poset1), (eps2,poset2),...]
        or the two keys
       "timeseriesfname" : path to a file containing the time series data from which to make posets
        "tsfile_is_row_format" : True if the time series file is in row format; False if in column format (see fileparsers.py)

    :return: Writes True (pattern match for the poset) or False (no pattern match) or
        parameter count (# successful matches) plus the number of parameters, for each
         epsilon to a dictionary keyed by network spec, which is dumped to a json file:
         { networkspec : (eps, result, num params) }
    '''
    #TODO: customize posets to networks (different numbers of nodes require different posets)
    if "posets" not in params:
        posets = createPosetsFromData(params['timeseriesfname'],params['epsilons'],params['tsfile_is_row_format'])
    else:
        posets = ast.literal_eval(params["posets"])
    results = {}
    for networkspec in networks:
        network = DSGRN.Network(networkspec)
        ER = []
        for (eps,(events,event_ordering)) in posets:
            paramgraph, patterngraph = getGraphs(events, event_ordering, network)
            R = globals()[params['matchingfunction']](paramgraph, patterngraph, params['count'])
            ER.append((eps,R,paramgraph.size()))
        results[networkspec] = ER
    rname = os.path.join(resultsdir,"pattern_matches.json")
    if os.path.exists(rname):
        os.rename(rname,rname+".old")
    json.dump(results,open(rname,'w'))


def createPosetsFromData(timeseriesfname,epsilons,row):
    '''
    Use min_interval_posets submodule to make a poset from a time series data file. See query for inputs.
    :return: list of (epsilon, poset) tuples
    '''
    if row:
        data,labels,times = fileparsers.parseTimeSeriesFileRow(timeseriesfname)
    else:
        data, labels, times = fileparsers.parseTimeSeriesFileCol(timeseriesfname)
    if len(set(labels)) < len(labels):
        raise("Non-unique names in time series file.")
    curves = {}
    for (L,D) in zip(labels,data):
        curves[L] = libposets.curve.Curve({t : d} for (t,d) in zip(times,D)).normalize()
    posets = libposets.posets.main(curves, epsilons)
    return posets


def getGraphs(events,event_ordering,network):
    '''
    Make pattern graph and parameter graph for the network and poset.
    '''
    poe = DSGRN.PosetOfExtrema(network,events,event_ordering)
    patterngraph = DSGRN.PatternGraph(poe)
    paramgraph = DSGRN.ParameterGraph(network)
    return paramgraph,patterngraph


def CycleMatchInStableMorseSet(paramgraph, patterngraph, count):
    '''
    Search for cycle matches in stable Morse sets only.
    :return: Integer count of parameters if count = True; if count = False return True if at least one match, False otherwise.
    '''
    numparams = 0
    for paramind in range(paramgraph.size()):
        domaingraph = DSGRN.DomainGraph(paramgraph.parameter(paramind))
        morsedecomposition = DSGRN.MorseDecomposition(domaingraph.digraph())
        morsegraph = DSGRN.MorseGraph(domaingraph,morsedecomposition)
        for i in range(0,morsedecomposition.poset().size()):
             if morsegraph.annotation(i)[0] in ["FC", "XC"] and len(morsedecomposition.poset().children(i)) == 0:
                searchgraph = DSGRN.SearchGraph(domaingraph,i)
                matchinggraph = DSGRN.MatchingGraph(searchgraph,patterngraph)
                if DSGRN.CycleMatch(matchinggraph):
                    if count:
                        numparams +=1
                        break
                    else:
                        return True
    return numparams if count else False


def CycleMatchInDomainGraph(paramgraph, patterngraph, count):
    '''
    Search for cycle matches anywhere in the domain graph.
    :return: Integer count of parameters if count = True; if count = False return True if at least one match, False otherwise.
    '''
    numparams = 0
    for paramind in range(paramgraph.size()):
        domaingraph = DSGRN.DomainGraph(paramgraph.parameter(paramind))
        searchgraph = DSGRN.SearchGraph(domaingraph)
        matchinggraph = DSGRN.MatchingGraph(searchgraph, patterngraph)
        if DSGRN.CycleMatch(matchinggraph):
            if count:
                numparams += 1
            else:
                return True
    return numparams if count else False


def PathMatchInDomainGraph(paramgraph, patterngraph, count):
    '''
    Search for path matches anywhere in the domain graph.
    :return: Integer count of parameters if count = True; if count = False return True if at least one match, False otherwise.
    '''
    numparams = 0
    for paramind in range(paramgraph.size()):
        domaingraph = DSGRN.DomainGraph(paramgraph.parameter(paramind))
        searchgraph = DSGRN.SearchGraph(domaingraph)
        matchinggraph = DSGRN.MatchingGraph(searchgraph, patterngraph)
        if DSGRN.PathMatch(matchinggraph):
            if count:
                numparams += 1
            else:
                return True
    return numparams if count else False
