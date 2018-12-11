import NetworkPerturbations.perturbations.networkperturbations as netper
import NetworkPerturbations.perturbations.fileparsers as fp
import NetworkPerturbations.queries.MultistabilityExists as ME
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
        "time_to_wait" : 7200,
        "maxparams" : 10000,
        "filters" : [{"constrained_inedges" : {"min_inedges" : 1, "max_inedges" : 2}}, {"is_feed_forward" : {}}]
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
    print("Saving feed-forward networks.")
    json.dump(networks,open("temp/all_networks_tested.json","w"))
    # print("Searching for truth tables...")
    # ME.query(networks,"temp",query_params)

if __name__ == "__main__":
    run()