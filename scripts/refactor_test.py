import NetworkPerturbations.perturbations.networkperturbations as netper
import NetworkPerturbations.perturbations.fileparsers as fp
from pprint import pprint
from NetworkPerturbations.queries.CountFPMatch import query
import DSGRN
import random

def run():
    network_spec = "X1 : (X1)(~X3)\nX2 : X1\nX3 : X1 + X2"

    params = {
        "edgelist" : fp.parseEdgeFile("../tests/edgefile_X1X2X3.txt"),
        "nodelist" : fp.parseNodeFile("../tests/nodefile_X1X2X3.txt"),
        "probabilities" : {"addNode" : 0.30, "removeNode" : 0.00, "addEdge" : 0.70, "removeEdge" : 0.00},
        "range_operations" : [1,3],
        "numperturbations": 3,
        "maxparams": 5000,
        "time_to_wait": 5
    }

    networks = netper.perturbNetwork(params,network_spec)
    for n in networks:
        pprint(n)
        print("Number of parameters is {}.\n".format(DSGRN.ParameterGraph(DSGRN.Network(n)).size()))

    query(networks,"temp",{"bounds":{"X1":[2,2],"X2":[1,1],"X3":[0,1]}})

if __name__ == "__main__":
    run()