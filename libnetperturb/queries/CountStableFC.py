import DSGRN
import os, json

def query(networks,resultsdir,params):
    '''
    :param networks: list of network specification strings in DSGRN format
    :param resultsdir: path to directory where results file(s) will be stored
    :param params: unused argument, present for API reasons

    :return: Writes count of parameters with a stable FC to a dictionary keyed by
    network spec, which is dumped to a json file.
    '''
    rname = os.path.join(resultsdir,"Stable_FC_parameter_counts.json")
    if os.path.exists(rname):
        os.rename(rname,rname+".old")

    def is_FC(annotation):
        return annotation.startswith("FC")

    resultsdict = {}
    for net in networks:
        count = 0
        network = DSGRN.Network()
        network.assign(net)
        parametergraph = DSGRN.ParameterGraph(network)
        for p in range(parametergraph.size()):
            parameter = parametergraph.parameter(p)
            dg = DSGRN.DomainGraph(parameter)
            md = DSGRN.MorseDecomposition(dg.digraph())
            mg = DSGRN.MorseGraph(dg, md)
            stable_FC_annotations = [mg.annotation(i)[0] for i in range(0, mg.poset().size())
                                     if is_FC(mg.annotation(i)[0]) and len(mg.poset().children(i)) == 0]
            if len(stable_FC_annotations) > 0:
                count+=1
        resultsdict[net] = str(count)+"/"+str(parametergraph.size())
        json.dump(resultsdict,open(rname,'w'))

