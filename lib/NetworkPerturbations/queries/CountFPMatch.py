import DSGRN
import os, json

def query(networks,resultsdir,params):
    '''
    :param networks: list of network specification strings in DSGRN format
    :param resultsdir: path to directory where results file(s) will be stored
    :param params: dictionary containing the key "bounds". bounds is a dictionary
    of variable names common to all network specifications with a range of values
    assigned to each. Example: {"X1":[2,2],"X2":[1,1],"X3":[0,1]}. The integer ranges
    are the matching conditions for an FP. For example, if there are four variables
    X1, X2, X3, X4 in the network spec, the FP (2,1,0,*) would be a match for any
    value of *.

    :return: Writes count of parameters with an FP match to a dictionary keyed by
    network spec, which is dumped to a json file.
    '''
    #TODO: parallelize

    bounds = dict(params["bounds"])

    def is_FP(annotation):
        return annotation.startswith("FP")

    def is_FP_match(bounds_ind, annotation):
        digits = [int(s) for s in annotation.replace(",", "").split() if s.isdigit()]
        return all(digits[k] >= bounds_ind[k][0] and digits[k] <= bounds_ind[k][1]
               for k in bounds_ind)

    resultsdict = {}
    for net in networks:
        count = 0
        network = DSGRN.Network()
        network.assign(net)
        bounds_ind = {network.index(str(k)): bounds[k] for k in bounds}
        parametergraph = DSGRN.ParameterGraph(network)
        for p in range(parametergraph.size()):
            parameter = parametergraph.parameter(p)
            dg = DSGRN.DomainGraph(parameter)
            md = DSGRN.MorseDecomposition(dg.digraph())
            mg = DSGRN.MorseGraph(dg, md)
            stable_FP_annotations = [mg.annotation(i)[0] for i in range(0, mg.poset().size())
                                     if is_FP(mg.annotation(i)[0]) and len(mg.poset().children(i)) == 0]
            if any([is_FP_match(bounds_ind,a) for a in stable_FP_annotations]):
                count+=1
        resultsdict[net] = [count,parametergraph.size()]

    rname = os.path.join(resultsdir,"query_results.json")
    if os.path.exists(rname):
        os.rename(rname,rname+".old")
    json.dump(resultsdict,open(rname,'w'))

