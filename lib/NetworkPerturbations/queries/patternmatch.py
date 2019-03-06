import DSGRN
import json, os, ast, warnings
from min_interval_posets import curve
from min_interval_posets import posets as make_posets
import pandas as pd
from multiprocessing import Pool
from copy import deepcopy
from functools import partial


def query(networks,resultsdir,params):
    '''
    For each epsilon in a list of epsilons, a poset from time series data is created. This poset is matched against the
    domain graph for each parameter in each network from a list of networks. The result is True if there is at least one
    match, False if not, or a count of the number of parameters with a match.

    :param networks: list of network specification strings in DSGRN format
    :param resultsdir: path to directory where results file(s) will be stored
    :param params: A dictionary containing the keys
        "matchingfunction" : a string containing the name of one of the matching functions in this module
        "count" : True or False, whether to count all params or shortcut at first success
        Then, one can either specify posets directly, or extract posets from timeseries data.
        Include EITHER
        "posets" : a (quoted) dictionary of Python tuples of node names keying a list of tuples of epsilon with a DSGRN
        formatted poset:
                    '{ ("A","B","C") : [(eps11,poset11), (eps21,poset21),...], ("A","B","D") : [(eps12,poset12), (eps22,
                    poset22),...] }' (the quotes are to handle difficulties with the json format)
        OR the three keys
        "timeseriesfname" : path to a file containing the time series data from which to make posets
        "tsfile_is_row_format" : True if the time series file is in row format (times are in the first row); False if in
        column format (times are in the first column)
        "epsilons" : list of floats 0 <= x <= 1, one poset will be made for each x

    :return: Writes True (pattern match for the poset) or False (no pattern match) or
        parameter count (# successful matches) plus the number of parameters, for each
         epsilon to a dictionary keyed by network spec, which is dumped to a json file:
         { networkspec : (eps, result, num params) }
    '''

    if "posets" not in params:
        posets,networks = calculate_posets(params,networks)
    else:
        lit_posets = ast.literal_eval(params["posets"])
        posets = {}
        for names,pos in lit_posets.items():
            # make sure variables are in canonical order
            sort_names = tuple(sorted(list(names)))
            posets[sort_names] = pos

    pool = Pool()  # Create a multiprocessing Pool
    output = pool.map(partial(search_over_networks, params, posets,len(networks)),enumerate(networks))
    results = dict(output)
    rname = os.path.join(resultsdir,"query_results.json")
    if os.path.exists(rname):
        os.rename(rname,rname+".old")
    json.dump(results,open(rname,'w'))


def search_over_networks(params,posets,N,tup):
    (k, netspec) = tup
    print("Network {} of {}".format(k+1, N))
    network = DSGRN.Network(netspec)
    names = tuple(sorted([network.name(k) for k in range(network.size())]))
    ER = []
    for (eps, (events, event_ordering)) in posets[names]:
        # TODO: In order for cycle matches to work correctly, the last extremum on each time series with an odd number of extrema must be removed
        paramgraph, patterngraph = getGraphs(events, event_ordering, network)
        # TODO: Use inspect module instead of globals()
        R = globals()[params['matchingfunction']](paramgraph, patterngraph, params['count'])
        ER.append((eps, R, paramgraph.size()))
    return (netspec, ER)


def calculate_posets(params,networks):
    data, times = readrow(params['timeseriesfname']) if params['tsfile_is_row_format'] else readcol(
        params['timeseriesfname'])
    posets = {}
    new_networks = []
    missing_names = set([])
    for networkspec in networks:
        network = DSGRN.Network(networkspec)
        names = tuple(sorted([network.name(k) for k in range(network.size())]))
        missing_names = missing_names.union(set(name for name in names if name not in data))
        if set(names).intersection(missing_names):
            continue
        if names not in posets.keys():
            curves = [curve.Curve(data[name], times, True) for name in names]
            pos = make_posets.eps_posets(dict(zip(names,curves)), params["epsilons"])
            if pos is None:
                raise ValueError("poset is None!")
            posets[names] = pos
        new_networks.append(networkspec)
    if missing_names:
        print("No time series for nodes {}. Skipping all networks with at least one missing time series.\nContinuing with {} networks.".format(missing_names,len(new_networks)))
    return posets, new_networks


def extractdata(filename):
    file_type = filename.split(".")[-1]
    if file_type == "tsv":
        df = pd.read_csv(open(filename),comment="#",delim_whitespace=True)
    elif file_type == "csv":
        df = pd.read_csv(open(filename),comment="#")
    else:
        raise ValueError("File type not recognized. Require .tsv or .csv.")
    return list(df)[1:],df.values


def readrow(filename):
    times,data = extractdata(filename)
    times = [float(n) for n in times]
    names = data[:,0]
    if len(set(names)) < len(names):
        raise ValueError("Non-unique names in time series file.")
    return dict(zip(names,[data[k,1:] for k in range(data.shape[0])])), times


def readcol(filename):
    names,data = extractdata(filename)
    if len(set(names)) < len(names):
        raise ValueError("Non-unique names in time series file.")
    times = data[:,0]
    return dict(zip(names,[data[1:,k] for k in range(data.shape[1])])), times


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


def PathMatchInStableFullCycle(paramgraph, patterngraph, count):
    '''
    Search for path matches in stable full cycles only.
    :return: Integer count of parameters if count = True; if count = False return True if at least one match, False otherwise.
    '''
    numparams = 0
    for paramind in range(paramgraph.size()):
        domaingraph = DSGRN.DomainGraph(paramgraph.parameter(paramind))
        morsedecomposition = DSGRN.MorseDecomposition(domaingraph.digraph())
        morsegraph = DSGRN.MorseGraph(domaingraph,morsedecomposition)
        for i in range(0,morsedecomposition.poset().size()):
             if morsegraph.annotation(i)[0]  == "FC" and len(morsedecomposition.poset().children(i)) == 0:
                searchgraph = DSGRN.SearchGraph(domaingraph,i)
                matchinggraph = DSGRN.MatchingGraph(searchgraph,patterngraph)
                if DSGRN.PathMatch(matchinggraph):
                    if count:
                        numparams +=1
                        break
                    else:
                        return True
    return numparams if count else False

