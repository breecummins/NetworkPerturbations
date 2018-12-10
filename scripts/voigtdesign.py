import NetworkPerturbations.perturbations.networkperturbations as netper
import NetworkPerturbations.perturbations.fileparsers as fp
import NetworkPerturbations.perturbations.graphtranslation as gt
import NetworkPerturbations.queries.MultistabilityExists as ME
import networkx as nx
import json


def run():
    network_spec = "C : C : E\nB : B : E\nA : A : E\nx : A : E\ny : B : E\nz : C : E\nYFP : : E\nD : D + " \
                    "YFP : E"
    params = {
        "edgelist" : fp.parseEdgeFile("VoigtEdgeFileShort.txt"),
        "nodelist" : fp.parseNodeFile("VoigtNodeFile.txt"),
        "probabilities" : {"addNode" : 0.5, "removeNode" : 0.00, "addEdge" : 0.5, "removeEdge" : 0.00},
        "range_operations" : [4,16],
        "numperturbations" : 10000,
        "time_to_wait" : 10,
        "maxparams" : 10000,
        "filters" : [{"constrained_inedges" : {"min_inedges" : 1, "max_inedges" : 3}}]
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
    print("Saving feed-forward networks.")
    json.dump(filtered_networks,open("temp/all_networks_tested.json","w"))
    # print("Searching for truth tables...")
    # ME.query(filtered_networks,"temp",query_params)

if __name__ == "__main__":
    run()