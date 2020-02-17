import DSGRN
import os, json, multiprocessing,sys,subprocess
from functools import partial

def query(networks,resultsdir,params):
    '''
    :param networks: list of network specification strings in DSGRN format
    :param resultsdir: path to directory where results file(s) will be stored
    :param params: dictionary with key "num_proc" that specifies the (integer) number of processes to be created in the multiprocessing tools.

    :return: Writes count of parameters with a stable FC to a dictionary keyed by
    network spec, which is dumped to a json file.
    '''

    resultsdict = {}
    for k,netspec in enumerate(networks):
        with open("temp.txt","w") as f:
            f.write(netspec)
        subprocess.call("mpiexec --oversubscribe -n {} Signatures {} {}".format(params["num_proc"],"temp.txt","temp.db"),shell=True)
        db = DSGRN.Database("temp.db")
        N = db.parametergraph.size()
        matches = len(DSGRN.StableFCQuery(db).matches())
        resultsdict[netspec] = (matches,N)
        rname = os.path.join(resultsdir,"query_results.json")
        if os.path.exists(rname):
            os.rename(rname,rname+".old")
        json.dump(resultsdict,open(rname,'w'))
        subprocess.call(["rm","temp.db"])
        subprocess.call(["rm","temp.txt"])
        print("Network {} of {} complete".format(k + 1, len(networks)))
        sys.stdout.flush()