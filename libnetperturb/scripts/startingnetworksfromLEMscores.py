import libnetperturb.perturbations.graphtranslation as gt
import numpy as np
from scipy.sparse.csgraph import connected_components
import pandas as pd


#FIXME: Relax so that nodes with no in-edges are allowed


def generate_lem_networks(threshold, lemfile):
    source, target, type_reg=parse_lem_file(threshold, lemfile)
    genes = sorted(set(source).intersection(target))
    print(genes, "\n")
    graph = makegraph(genes, source, target, type_reg)
    scc = strongly_connected_components(graph)
    networks = []
    for comp in scc:
        sg = gt.Graph()
        for v in comp:
            sg.add_vertex(comp.index(v),label=graph.vertex_label(v))
        for e in graph.edges():
            if e[0] in comp and e[1] in comp:
                sg.add_edge(comp.index(e[0]),comp.index(e[1]),label=graph.edge_label(*e))
        networks.append(gt.createEssentialNetworkSpecFromGraph(sg))
    return networks


def makegraph(genes,source,target,type_reg):
    # make gt.Graph
    graph = gt.Graph()
    for k,g in enumerate(genes):
        graph.add_vertex(k,label=g)
    for s, t, tr in zip(source,target,type_reg):
        if s in genes and t in genes:
            graph.add_edge(genes.index(s),genes.index(t),label=tr)
    return graph


def strongly_connected_components(graph):
    N = graph.size()
    adjacencymatrix=np.zeros((N,N))
    for (i,j) in graph.edges():
        adjacencymatrix[i,j]=1
    _, components = connected_components(adjacencymatrix,directed=True,connection="strong")
    components = list(components)
    grouped_components = [[k for k, c in enumerate(components) if c == d] for d in range(max(components) + 1) if components.count(d) > 1]
    return grouped_components


def parse_lem_file(threshold, fname, delimiter="\s+",comment="#"):
    # returns the source, target, type of regulation, and LEM score sorted by increasing normalized loss (LEM score).
    # Smaller scores are higher ranking.
    # Comment lines are denoted by "#", or change default argument for comment
    # Columns are whitespace delimited, or change default argument for delimiter
    # file format must have the following columns:
    # model:  TARGET_GENE = TYPE_REG(SOURCE_GENE)
    # norm_loss: numerical score
    df = pd.read_csv(fname,sep=delimiter,comment=comment)
    models = list(df["model"].values)
    LEM_score = list(df["norm_loss"].values)
    source=[]
    type_reg=[]
    target=[]
    for m in models:
        first = m.split("=")
        source.append(first[0])
        second = m.split("(")
        type_reg.append(second[0])
        target.append(second[1][:-1])
    [LEM_score, source, target, type_reg] = gt.sort_by_list(LEM_score, [source,target,type_reg], reverse=False)
    ind = next(k for k,l in enumerate(LEM_score) if l < threshold)
    return source[ind:], target[ind:], type_reg[ind:]


if __name__ == "__main__":
    lemfile = "all_scores_rep_0.tsv"
    threshold = 0.5
    print(generate_lem_networks(threshold, lemfile))