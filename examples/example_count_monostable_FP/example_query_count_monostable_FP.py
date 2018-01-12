# code that counts all parameter matches to a particular FP that is monostable

import DSGRN
import os, json

bounds = {"X1":[2,2],"X2":[1,1],"X3":[0,1]}


def query(networks,resultsdir):
    rname = os.path.join(resultsdir,"FP_parameter_match_counts.json")
    if os.path.exists(rname):
        os.rename(rname,rname+".old")

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
        bounds_ind = {network.index(k): bounds[k] for k in bounds}
        parametergraph = DSGRN.ParameterGraph(network)
        for p in range(parametergraph.size()):
            parameter = parametergraph.parameter(p)
            dg = DSGRN.DomainGraph(parameter)
            md = DSGRN.MorseDecomposition(dg.digraph())
            mg = DSGRN.MorseGraph()
            mg.assign(dg, md)
            stable_FP_annotations = [mg.annotation(i)[0] for i in range(0, mg.poset().size())
                                     if is_FP(mg.annotation(i)[0]) and len(mg.poset().children(i)) == 0]
            # monostable = len(stable_annotations) == 1
            if any([is_FP_match(bounds_ind,a) for a in stable_FP_annotations]):
                count+=1
        resultsdict[net] = count
        json.dump(resultsdict,open(rname,'w'))

