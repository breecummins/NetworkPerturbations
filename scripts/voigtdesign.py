import NetworkPerturbations.perturbations.networkperturbations as netper
import NetworkPerturbations.perturbations.fileparsers as fp
import NetworkPerturbations.perturbations.graphtranslation as gt
import NetworkPerturbations.queries.MultistabilityExists as ME
import networkx as nx
import random
from pprint import pprint


def run():
    network_spec = "A : A : E\nB : B : E\nC : C : E\nx : A : E\ny : B : E\nz : C : E\nYFP : : E\nD : D + YFP : E"

    params = {
        "edgelist" : fp.parseEdgeFile("VoigtEdgeFileShort.txt"),
        "nodelist" : fp.parseNodeFile("VoigtNodeFile.txt"),
        "add_anon_nodes" : False,
        "swap_edge_reg" : False,
        "minaddspergraph" : 4,
        "maxaddspergraph" : 12,
        "maxinedges" : 3,
        "numperturbations" : 10000,
        "time_to_wait" : 300,
        "maxparams" : 10000
    }

    query_params = {
        "included_bounds" : [{"C": [0, 0], "B": [0, 0], "A": [0, 0], "YFP": [1, 1]},
                             {"C": [0, 0], "B": [0, 0], "A": [2, 7], "YFP": [0, 0]},
                             {"C": [0, 0], "B": [2, 7], "A": [0, 0], "YFP": [1, 1]},
                             {"C": [0, 0], "B": [2, 7], "A": [2, 7], "YFP": [0, 0]},
                             {"C": [2, 7], "B": [0, 0], "A": [0, 0], "YFP": [0, 0]},
                             {"C": [2, 7], "B": [0, 0], "A": [2, 7], "YFP": [0, 0]},
                             {"C": [2, 7], "B": [2, 7], "A": [0, 0], "YFP": [0, 0]},
                             {"C": [2, 7], "B": [2, 7], "A": [2, 7], "YFP": [1, 1]}],
         "excluded_bounds" :[{"C": [0, 0], "B": [0, 0], "A": [0, 0], "YFP": [0, 0]},
                             {"C": [0, 0], "B": [0, 0], "A": [2, 7], "YFP": [1, 1]},
                             {"C": [0, 0], "B": [2, 7], "A": [0, 0], "YFP": [0, 0]},
                             {"C": [0, 0], "B": [2, 7], "A": [2, 7], "YFP": [1, 1]},
                             {"C": [2, 7], "B": [0, 0], "A": [0, 0], "YFP": [1, 1]},
                             {"C": [2, 7], "B": [0, 0], "A": [2, 7], "YFP": [1, 1]},
                             {"C": [2, 7], "B": [2, 7], "A": [0, 0], "YFP": [1, 1]},
                             {"C": [2, 7], "B": [2, 7], "A": [2, 7], "YFP": [0, 0]}]
    }

    networks = netper.perturbNetwork(params,network_spec)
    filtered_networks = []
    for ns in networks:
        graph = gt.getGraphFromNetworkSpec(ns)
        G = nx.DiGraph()
        G.add_edges_from(graph.edges())
        scc = nx.strongly_connected_components(G)
        # throw out graphs with non-trivial cycles
        if all(len(s) == 1 for s in scc):
            filtered_networks.append(ns)
    print("Number of filtered networks: {}".format(len(filtered_networks)))
    # for _ in range(10):
    #     print("\n")
    #     pprint(random.choice(filtered_networks))

    print("Searching for truth tables...")
    # ME.query(networks[1:],"temp",query_params)
    ME.query(networks[1:],"temp",query_params)

if __name__ == "__main__":
    run()