import DSGRN
import os, json, multiprocessing,sys
from functools import partial

def query(networks,resultsdir,params):
    '''
    :param networks: list of network specification strings in DSGRN format
    :param resultsdir: path to directory where results file(s) will be stored
    :param params: optional dictionary with key "num_proc" that specifies the (integer) number of processes to be created in the multiprocessing tools. Default: determined by cpu count.

    :return: Writes count of parameters with a stable FC to a dictionary keyed by
    network spec, which is dumped to a json file.
    '''

    num_proc = multiprocessing.cpu_count() if "num_proc" not in params else params["num_proc"]
    pool = multiprocessing.Pool(num_proc)  # Create a multiprocessing Pool
    output = pool.map(partial(check_FC,len(networks)),enumerate(networks))
    rname = os.path.join(resultsdir,"query_results.json")
    if os.path.exists(rname):
        os.rename(rname,rname+".old")
    json.dump(dict(output),open(rname,'w'))


def is_FC(annotation):
    return annotation.startswith("FC")


def check_FC(N,tup):
    k,netspec = tup
    print("Network {} of {}".format(k+1, N))
    sys.stdout.flush()
    count = 0
    network = DSGRN.Network(netspec)
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
    return netspec,(count,parametergraph.size())

