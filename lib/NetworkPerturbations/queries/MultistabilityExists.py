import DSGRN
import os, json, progressbar, sys
import multiprocessing
from functools import partial
import NetworkPerturbations.queries.query_utilities as qu

def query(networks,resultsdir,params):
    '''
    Take the intersection of an arbitrary number of DSGRN fixed points in a list.

    :param networks: list of network specification strings in DSGRN format
    :param resultsdir: path to directory where results file(s) will be stored
    :param params: dictionary containing the keys "included_bounds", "excluded_bounds", and optionally "hex_constraints".
                    The "bounds" variables are each a list of dictionaries of variable names common to all network
                    specifications with an associated integer range.
                    Example: [{"X1":[2,2],"X2":[1,1],"X3":[0,1]},{"X1":[0,1],"X2":[1,1],"X3":[2,3]}]
                    The integer ranges are the matching conditions for an FP.
                    For example, if there are four variablesm X1, X2, X3, X4 in the network spec,
                    the FP (2,1,0,*) would be a match to the first fixed point for any value of *.
                    The optional key "hex_constraints" is a dictionary of lists keying a tuple of two integers to a list
                    of hex numbers.
                    The tuple key describes the node type: (num inedges, num outedges) and the list contains the
                    allowable hex codes for this node type. In the algorithm below, only those hex codes in the list
                    are permitted for the node type.
                    Example: {(1,2) : ["C"], (3,1) : ["0"]} means that any node with 1 in-edge and 2 out-edges must have
                    hex code 0x0C and any node with 3 in-edges and 1 outedge must have hex code 0.
            Optional: "num_proc" specifies the number of processes to be created in the multiprocessing tools. Default: determined by cpu count.

    :return: List of network specs that match all FPs in params["included_bounds"] and match none of
             the FPs in params["excluded_bounds"] for at least 1 parameter that is dumped to a json file.
             NOTE: This means that no matches returns an empty list.
    '''

    included_bounds = [dict(b) for b in params["included_bounds"]]
    excluded_bounds = [dict(b) for b in params["excluded_bounds"]]
    num_proc = multiprocessing.cpu_count() if "num_proc" not in params else params["num_proc"]
    pool = multiprocessing.Pool(num_proc)  # Create a multiprocessing Pool
    if "hex_constraints" in params and params["hex_constraints"]:
        hex_constraints = dict(params["hex_constraints"])
        output = pool.map(partial(compute_for_network_with_constraints, included_bounds, excluded_bounds, len(networks), hex_constraints),enumerate(networks))
    else:
        output = pool.map(partial(compute_for_network_without_constraints, included_bounds, excluded_bounds, len(networks)),enumerate(networks))
    results = list(filter(None,output))
    rname = os.path.join(resultsdir,"query_results.json")
    if os.path.exists(rname):
        os.rename(rname,rname+".old")
    json.dump(results,open(rname,'w'))


def compute_for_network_without_constraints(included_bounds,excluded_bounds,N,tup):
    netspec,network, parametergraph = getpg(tup,N)
    # for p in progressbar.ProgressBar()(range(parametergraph.size())):
    for p in range(parametergraph.size()):
        if have_match(network, parametergraph.parameter(p), included_bounds, excluded_bounds):
            return netspec
    return None


def compute_for_network_with_constraints(included_bounds,excluded_bounds,N,hex_constraints,tup):
    netspec,network, parametergraph = getpg(tup,N)
    # for p in progressbar.ProgressBar()(range(parametergraph.size())):
    for p in range(parametergraph.size()):
        param = parametergraph.parameter(p)
        if qu.satisfies_hex_constraints(param,hex_constraints) and have_match(network, param, included_bounds,excluded_bounds):
            return netspec
    return None


def getpg(tup,N):
    (k, netspec) = tup
    print("Network {} of {}".format(k+1, N))
    sys.stdout.flush()
    network = DSGRN.Network(netspec)
    parametergraph = DSGRN.ParameterGraph(network)
    return netspec,network,parametergraph


def have_match(network,parameter,included_bounds,excluded_bounds):
    stable_FP_annotations = DSGRN_Computation(parameter)
    included = all_included(network, included_bounds, stable_FP_annotations)
    excluded = all_excluded(network, excluded_bounds, stable_FP_annotations)
    if included and excluded:
        return True
    return False


def DSGRN_Computation(parameter):
    dg = DSGRN.DomainGraph(parameter)
    md = DSGRN.MorseDecomposition(dg.digraph())
    mg = DSGRN.MorseGraph(dg, md)
    return [mg.annotation(i)[0] for i in range(0, mg.poset().size()) if is_FP(mg.annotation(i)[0]) and len(mg.poset(
        ).children(i)) == 0]


def is_FP(annotation):
    return annotation.startswith("FP")


def is_FP_match(bounds_ind, annotation):
    digits = [int(s) for s in annotation.replace(",", "").split() if s.isdigit()]
    return all(digits[k] >= bounds_ind[k][0] and digits[k] <= bounds_ind[k][1]
           for k in bounds_ind)


def is_multistable_match(network,b,stable_FP_annotations):
    bounds_ind = {network.index(str(k)): b[k] for k in b}
    return any([is_FP_match(bounds_ind, a) for a in stable_FP_annotations])


def all_included(network,included_bounds,stable_FP_annotations):
    for b in included_bounds:
        if not is_multistable_match(network, b, stable_FP_annotations):
            return False
    return True


def all_excluded(network,excluded_bounds,stable_FP_annotations):
    for b in excluded_bounds:
        if is_multistable_match(network, b, stable_FP_annotations):
            return False
    return True

