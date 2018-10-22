import libnetperturb.perturbations.graphtranslation as gt
import numpy as np
from scipy.sparse.csgraph import connected_components
import pandas as pd


def generate_lem_networks(lemfile, column, delimiter=None,comment="#"):
    '''

    :param lemfile: file name with lem scores; full path required if not in local folder
    :param column: a tuple containing column name of desired lem score, if the desired scores are lower "<" or
    higher ">" than the threshold, and the threshold itself.
    Examples: column=("norm_loss","<",0.4), column=("pld",">",0.1)
    :param delimiter: "\s+" for tab-delimited or "," for comma-delimited; if None it will be inferred from file type
    where possible
    :param comment: comment character in file, usually "#"

    :return: a list of network strings in DSGRN format
    '''
    source, target, type_reg=parse_lem_file(lemfile,column,delimiter,comment)
    genes = sorted(set(source).intersection(target))
    # print(genes, "\n")
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


def parse_lem_file(fname,column,delimiter=None,comment="#"):
    '''
    Parses lem score file of the following format:

    Any number of comment lines denoted starting with comment character(s)
    Columns delimited by delimiter character(s), or inferred by file type
    File must have the following column:
    model:  TARGET_GENE = TYPE_REG(SOURCE_GENE)
            Activating TYPE_REG must have an "a" or "A" in the string, and no "r" or "R"
            Repressing TYPE_REG must have an "r" or "R" in the string, and no "a" or "A"

    :param lemfile: file name with lem scores; full path required if not in local folder
    :param column: a tuple containing column name of desired lem score, if the desired scores are lower "<" or
    higher ">" than the threshold, and the threshold itself.
    Examples: column=("norm_loss","<",0.4), column=("pld",">",0.1)
    The column name column[0] must be in the file.
    :param delimiter: "\s+" for tab-delimited or "," for comma-delimited; if None it will be inferred from file type
    :param comment: comment character in file, usually "#"

    :return: three lists containing the sources, targets, and types of regulation sorted by LEM score

    '''

    if delimiter is None:
        ext = fname.split(".")[-1]
        if ext == "tsv":
            delimiter = "\s+"
        elif ext == "csv":
            delimiter = ","
        else:
            raise ValueError("Extension .{} not recognized. Please specify delimiter.".format(ext))
    df = pd.read_csv(fname,sep=delimiter,comment=comment)
    models = list(df["model"].values)
    LEM_score = list(df[column[0]].values)
    source=[]
    type_reg=[]
    target=[]
    for m in models:
        first = m.split("=")
        target.append(first[0])
        second = first[1].split("(")
        reg = second[0]
        if ("a" in reg or "A" in reg) and not("r" in reg or "R" in reg):
            type_reg.append("a")
        elif ("r" in reg or "R" in reg) and not("a" in reg or "A" in reg):
            type_reg.append("r")
        else:
            raise ValueError("Regulation type is ambiguous. Regulation must be a string with 'a' and no 'r' for activation and 'r' with no 'a' for repression.")
        source.append(second[1][:-1])
    if column[1] == "<":
        [LEM_score, source, target, type_reg] = gt.sort_by_list(LEM_score,[source, target, type_reg], reverse=False)
        ind = next(k for k,l in enumerate(LEM_score) if l > column[2])
    elif column[1] == ">":
        [LEM_score, source, target, type_reg] = gt.sort_by_list(LEM_score, [source, target, type_reg], reverse=True)
        ind = next(k for k, l in enumerate(LEM_score) if l < column[2])
    else:
        raise ValueError("Second element of input argument 'column' must be '<' or '>'.")
    return source[:ind], target[:ind], type_reg[:ind]


if __name__ == "__main__":
    lemfile = "all_scores_rep_0.tsv"
    # print(parse_lem_file(lemfile,("norm_loss","<",0.4)))
    print(generate_lem_networks(lemfile,("norm_loss","<",0.4)))

    # print(parse_lem_file(lemfile,("pld","<",0.1)))
    print(generate_lem_networks(lemfile,("pld",">",0.01)))





