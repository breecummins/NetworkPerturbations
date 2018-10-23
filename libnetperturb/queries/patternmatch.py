import DSGRN
import sys, json, os, ast
sys.path.append('../../min_interval_posets')
from min_interval_posets.libposets import curve
from min_interval_posets.libposets import posets as make_posets
import pandas as pd
from copy import deepcopy

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
        "tsfile_is_row_format" : True if the time series file is in row format (times are in the first row); False if in
        column format (times are in the first column)

    :return: Writes True (pattern match for the poset) or False (no pattern match) or
        parameter count (# successful matches) plus the number of parameters, for each
         epsilon to a dictionary keyed by network spec, which is dumped to a json file:
         { networkspec : (eps, result, num params) }
    '''
    if "posets" not in params:
        curves = readrow(params['timeseriesfname']) if params['tsfile_is_row_format'] else readcol(params['timeseriesfname'])
        all_posets = []
        all_names = []
    else:
        posets = ast.literal_eval(params["posets"])
    results = {}
    for networkspec in networks:
        network = DSGRN.Network(networkspec)
        if "posets" not in params:
            names = set(list(network.name(k) for k in range(network.size())))
            if names not in all_names:
                posets = createPosetsFromData(names, curves, params['epsilons'])
                all_posets.append(posets)
                all_names.append(names)
            else:
                ind = all_names.index(names)
                posets = all_posets[ind]
        ER = []
        for (eps,(events,event_ordering)) in posets:
            #TODO: In order for cycle matches to work correctly, the last extremum on each time series with an odd number of extrema must be removed
            paramgraph, patterngraph = getGraphs(events, event_ordering, network)
            R = globals()[params['matchingfunction']](paramgraph, patterngraph, params['count'])
            ER.append((eps,R,paramgraph.size()))
        results[networkspec] = ER
    rname = os.path.join(resultsdir,"pattern_matches.json")
    if os.path.exists(rname):
        os.rename(rname,rname+".old")
    json.dump(results,open(rname,'w'))


def extractdata(filename):
    file_type = filename.split(".")[-1]
    if file_type == "tsv":
        df = pd.read_csv(open(filename),delim_whitespace=True)
    elif file_type == "csv":
        df = pd.read_csv(open(filename))
    else:
        raise ValueError("File type not recognized. Require .tsv or .csv.")
    return list(df)[1:],df.values


def readrow(filename):
    times,data = extractdata(filename)
    times = [float(n) for n in times]
    names = data[:,0]
    if len(set(names)) < len(names):
        raise ValueError("Non-unique names in time series file.")
    curves = [curve.Curve(data[k,1:],times,True) for k in range(data.shape[0])]
    return dict(zip(names,curves))


def readcol(filename):
    names,data = extractdata(filename)
    if len(set(names)) < len(names):
        raise ValueError("Non-unique names in time series file.")
    times = data[:,0]
    curves = [curve.Curve(data[1:,k],times,True) for k in range(data.shape[1])]
    return dict(zip(names,curves))


def createPosetsFromData(names,curves,epsilons):
    '''
    Use min_interval_posets submodule to make a poset from time series curves. See query for inputs.
    :return: list of (epsilon, poset) tuples
    '''
    subset_curves = deepcopy(curves)
    for name in curves:
        if name not in names:
            subset_curves.pop(name)
    return make_posets.eps_posets(subset_curves, epsilons)


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
