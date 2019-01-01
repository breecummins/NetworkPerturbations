import NetworkPerturbations.perturbations.networkperturbations as netper
import NetworkPerturbations.perturbations.fileparsers as fp
import NetworkPerturbations.queries.MultistabilityExists as ME
import json, subprocess, sys, os


def run():
    network_spec = "C : C : E\nB : B : E\nA : A : E\nx : A : E\ny : B : E\nz : C : E\nYFP : : E\nD : D + " \
                    "YFP : E"
    params = {
        "edgelist" : fp.parseEdgeFile("VoigtEdgeFileShort_5node.txt"),
        "nodelist" : fp.parseNodeFile("VoigtNodeFile_5node.txt"),
        "probabilities" : {"addNode" : 0.8, "removeNode" : 0.00, "addEdge" : 0.2, "removeEdge" : 0.00},
        "range_operations" : [7,10],
        "numperturbations" : 100000,
        "time_to_wait" : 7200,
        "maxparams" : 50000,
        "filters" : {"constrained_outedges" : {"min_outedges" : 1, "max_outedges" : 4},
                     "constrained_inedges" : {"min_inedges" : 1, "max_inedges" : 2}, "is_feed_forward" : {},
                     }
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
                             {"C": [2, 7], "B": [2, 7], "A": [2, 7], "YFP": [0, 0]}],
        "hex_constraints" : {(1,1) : ["2"], (1,2) : ["C"], (1,3) : ["38"], (2,1) : ["E"], (2,2) : ["FC"], (2,3) : ["FF8"]}
    }

    datetime = subprocess.check_output(['date +%Y_%m_%d_%H_%M_%S'], shell=True).decode(sys.stdout.encoding).strip()
    outdir = "computations_"+datetime
    os.makedirs(outdir)

    def rerun():
        fname = "all_networks_tested.json"
        networks = json.load(open(fname))
        ME.query(networks, outdir, query_params)

    def perturb():
        networks = netper.perturbNetwork(params,network_spec)
        print("Saving feed-forward networks.")
        json.dump(networks,open(os.path.join(outdir,"all_networks_tested.json"),"w"))
        print("Searching for truth tables...")
        ME.query(networks,outdir,query_params)

    def check_original():
        original = ["C : C : E\nB : B : E\nA : A : E\nw : C : E\nz: A + C : E\ny : B : E\nx : A : E\nt : (~y)(~x) : E\nu : "
                 "~t : E\nv : (~w)(~u) : E\nYFP : (~v)(~z) : E\nD : YFP + D : E"]
        ME.query(original, "temp", query_params)
        net = json.load(open(os.path.join("temp","Networks_With_Multistable_FP.json")))
        if len(net) == 1:
            print("\nOriginal network passes FP search.")

    def check_extended():
        extended = ["C : C : E\nB : B : E\nA : A : E\nw : C : E\nz: A + C : E\ny : B : E\nx : A : E\nt : (~y)(~x) : E\nu : "
                 "~t : E\nv : (~w)(~u) : E\nYFP : (~v)(~z3) : E\nD : YFP + D : E\nz2 : ~z : E\nz3 : ~z2 : E"]
        ME.query(extended, "temp", query_params)
        net = json.load(open(os.path.join("temp","Networks_With_Multistable_FP.json")))
        if len(net) == 1:
            print("\nExtended network passes FP search.")

    # rerun()
    # perturb()
    # check_original()
    check_extended()

if __name__ == "__main__":
    run()