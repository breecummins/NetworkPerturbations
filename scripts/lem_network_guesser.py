import NetworkPerturbations.perturbations.graphtranslation as gt
import numpy as np
from scipy.sparse.csgraph import connected_components
import pandas as pd
import sys, ast,os
from inspect import getmembers, isfunction



def generate_lem_networks(lemfile, column, outputdir, func = "guarantee_strongly_connected", num_top_edges = 0, comment="#", return_networks=False):
    '''

    :param lemfile: file name with lem scores; full path required if not in local folder
    :param column: a tuple containing column name of desired lem score, if the desired scores are lower "<" or
    higher ">" than the threshold, the threshold for creating the seed network, and a second more permissive threshold
    for creating the node and edge files. If the second threshold is absent, then all nodes and edges will be included.
    Examples: column=("norm_loss","<",0.4,0.5), column=("pld",">",0.1,0.02)
    The column name column[0] must be in the file.
    :param outputdir: location for saving files
    :param comment: comment character in file, usually "#"
    :param return_networks: False = return file names, True = return network list, files are written in either case

    :return: a list of network strings in DSGRN format
    '''
    source, target, type_reg, nodefile, edgefile=parse_lem_file(lemfile,column,outputdir,comment)
    try:
        func_handle = globals()[func]
    except KeyError:
        print("The function {} is not implemented.".format(func))
        raise
    if num_top_edges:
        graph = makegraph(source, target, type_reg, num_top_edges)
    else:
        graph = makegraph(source,target,type_reg)
    networks = func_handle(graph)
    networkfile = os.path.join(outputdir,"lem_networks.txt")
    with open(networkfile,"w") as f:
        f.write(str(networks))
    if return_networks:
        return networks
    else:
        return nodefile, edgefile, networkfile


def guarantee_strongly_connected(graph):
    # x is a placeholder to guarantee consistent API
    scc = strongly_connected_components(graph)
    networks = []
    for comp in scc:
        sg = gt.Graph()
        for v in comp:
            sg.add_vertex(comp.index(v), label=graph.vertex_label(v))
        for e in graph.edges():
            if e[0] in comp and e[1] in comp:
                sg.add_edge(comp.index(e[0]), comp.index(e[1]), label=graph.edge_label(*e))
        networks.append(gt.createEssentialNetworkSpecFromGraph(sg))
    return networks


def choose_top_edges(graph):
    return gt.createEssentialNetworkSpecFromGraph(graph)


def makegraph(source,target,type_reg,x=0):
    # make gt.Graph
    edges = list(zip(source,target,type_reg))
    if x:
        edges = edges[:int(x)]
    genes = sorted(set(source).union(target))
    graph = gt.Graph()
    for k,g in enumerate(genes):
        graph.add_vertex(k,label=g)
    for s, t, tr in edges:
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


def sort_by_list(X, Y, reverse=False):
    # X is a list of length n, Y is a list of lists of length n
    # sort every list in Y by either ascending order (reverse = False) or descending order (reverse=True) of X
    newlists = [[] for _ in range(len(Y) + 1)]
    for ztup in sorted(zip(X, *Y), reverse=reverse):
        for k, z in enumerate(ztup):
            newlists[k].append(z)
    return newlists


def parse_lem_file(fname,column,outputdir,comment="#"):
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
    higher ">" than the threshold, the threshold for creating the seed network, and a second more permissive threshold
    for creating the node and edge files. If the second threshold is absent, then all nodes and edges will be included.
    Examples: column=("norm_loss","<",0.4,0.5), column=("pld",">",0.1,0.02)
    The column name column[0] must be in the file.
    :param delimiter: "\s+" for tab-delimited or "," for comma-delimited; if None it will be inferred from file type
    :param comment: comment character in file, usually "#"

    :return: three lists containing the sources, targets, and types of regulation sorted by LEM score

    '''

    ext = fname.split(".")[-1]
    if ext == "tsv":
        df = pd.read_csv(fname,delim_whitespace=True,comment=comment)
    elif ext == "csv":
        df = pd.read_csv(fname,comment=comment)
    else:
        raise ValueError("Extension .{} not recognized. Please specify delimiter.".format(ext))
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
        [LEM_score, source, target, type_reg] = sort_by_list(LEM_score,[source, target, type_reg], reverse=False)
        ind = next(k for k, l in enumerate(LEM_score) if l > column[2])
        try:
            jnd = next(k for k, l in enumerate(LEM_score) if l > column[3])
        except:
            jnd = len(source)
    elif column[1] == ">":
        [LEM_score, source, target, type_reg] = sort_by_list(LEM_score, [source, target, type_reg], reverse=True)
        ind = next(k for k, l in enumerate(LEM_score) if l < column[2])
        try:
            jnd = next(k for k, l in enumerate(LEM_score) if l < column[3])
        except:
            jnd = len(source)
    else:
        raise ValueError("Second element of input argument 'column' must be '<' or '>'.")
    if outputdir:
        nodefile = os.path.join(outputdir, "node_file.txt")
        edgefile = os.path.join(outputdir, "edge_file.txt")
    else:
        nodefile = "node_file.txt"
        edgefile = "edge_file.txt"
    with open(nodefile,"w") as f:
        f.write("\n".join(set(source).union(target)))
    with open(edgefile,"w") as f:
        f.write("\n".join(["{}={}({})".format(*e) for e in zip(target[:jnd],type_reg[:jnd],source[:jnd])]))
    return source[:ind], target[:ind], type_reg[:ind], nodefile, edgefile


if __name__ == "__main__":
    if len(sys.argv) > 5:
        generate_lem_networks(sys.argv[1], ast.literal_eval(sys.argv[2]),sys.argv[3],sys.argv[4],sys.argv[5])
    elif len(sys.argv) > 4:
        generate_lem_networks(sys.argv[1], ast.literal_eval(sys.argv[2]),sys.argv[3],sys.argv[4])
    elif len(sys.argv) > 3:
        generate_lem_networks(sys.argv[1], ast.literal_eval(sys.argv[2]),sys.argv[3])
    else:
        print("Arguments lemfile, column, and outputdir are required.")





