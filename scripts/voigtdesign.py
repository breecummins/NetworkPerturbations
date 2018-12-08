import NetworkPerturbations.perturbations.networkperturbations as netper
import NetworkPerturbations.perturbations.fileparsers as fp
import NetworkPerturbations.perturbations.graphtranslation as gt
import networkx as nx
from pprint import pprint

network_spec = "A : A : E\nB : B : E\nC : C : E\nx : A : E\ny : B : E\nz : C : E\nYFP : : E\nD : D + YFP : E"

params = {
    "edgelist" : fp.parseEdgeFile("VoigtEdgeFile.txt"),
    "nodelist" : fp.parseNodeFile("VoigtNodeFile.txt"),
    "add_anon_nodes" : False,
    "swap_edge_reg" : False,
    "minaddspergraph" : 4,
    "maxaddspergraph" : 12,
    "maxinedges" : 3,
    "numperturbations" : 10000,
    "time_to_wait" : 60,
    "maxparams" : 10000000
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