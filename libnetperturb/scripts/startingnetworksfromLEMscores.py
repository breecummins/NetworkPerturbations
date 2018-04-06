import libnetperturb.perturbations.graphtranslation as gt
import numpy as np
from scipy.sparse.csgraph import connected_components


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


def parse_lem_file(threshold, fname):
    # returns the source, target, type of regulation, and LEM score sorted by increasing sqrt loss/root score (LEM score). Smaller scores are higher ranking.
    # file format must be:
    # 1) optional comment lines denoted by #
    # 2) optional line of column headers in which column 2 does not have the header "="
    # 3) all following lines are data that begin with TARGET_GENE = TYPE_REG(SOURCE_GENE)
    # 4) sqrt loss / root score is the last numerical score (and word) on each data line
    source=[]
    type_reg=[]
    target=[]
    sqrtloss_root=[]
    with open(fname,'r') as f:
        for l in f.readlines():
            if l[0] == '#':
                continue
            wordlist=l.split()
            if wordlist[1] != "=":
                continue
            sqlr = float(wordlist[-1])
            if sqlr<threshold:
                target.append(wordlist[0])
                sqrtloss_root.append(sqlr)
                two_words=wordlist[2].split('(')
                type_reg.append(two_words[0])
                source.append(two_words[1][:-1])
    [_, source, target, type_reg] = gt.sort_by_list(sqrtloss_root, [source,target,type_reg], reverse=False)
    return source, target, type_reg


if __name__ == "__main__":
    lemfile = "wrair2015_v2_fpkm-p1_s19_90tfs_top25_dljtk_lem_scores.txt"
    threshold = 0.2
    print(generate_lem_networks(threshold, lemfile))