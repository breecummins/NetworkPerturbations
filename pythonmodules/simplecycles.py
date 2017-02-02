import re, subprocess, os, itertools
import networkx as nx
import intervalgraph as ig
import DSGRN
from makejobs import Job



block_question=re.compile("[?]+")
DI_min=re.compile("DI")
ID_max=re.compile("ID")

def get_min_max(ipath):
    # First handle explicit extrema
    imin = [m.start(0)+1 for m in DI_min.finditer(ipath)]
    imax = [m.start(0)+1 for m in ID_max.finditer(ipath)]
    # Now search for extrema in question mark blocks.
    # Assume no extra extrema in D???I (i.e. there's exactly one min that occurs somewhere in ???).
    # If ? at beginning and end of the path, add an extremum;
    # for example ???ID??? must have a min somewhere in the ?? if it's a cycle.
    extremum = tuple()
    for m in block_question.finditer(ipath):
        start, end = m.start(0), m.end(0)
        label1 = ipath[start-1] if start>0 else "?"
        label2 = ipath[end] if end<len(ipath) else "?"
        if label1+label2 == 'DI': imin += range(start,end+1)
        elif label1+label2 == 'ID': imax += range(start,end+1)
        elif label1 == "?": extremum = (label2,range(start,end+1))
        elif label2 == "?" and extremum: 
            if extremum[0] == "I" and label1 == "D": imin += extremum[1]+range(start,end)
            elif extremum[0] == "D" and label1 == "I": imax += extremum[1]+range(start,end)
    return sorted(imin), sorted(imax)

def make_consecutive_blocks(l):
    if not l: return l
    blocks, b, i = [], [l[0]], 1
    while i <= len(l):
        if i == len(l):
            blocks.append([b[0],b[-1]])
        elif l[i] - l[i-1] == 1:
            b += [l[i]]
        else:
            blocks.append([b[0],b[-1]])
            b = [l[i]]
        i += 1
    return blocks

def make_partial_orders(cycles,names):
    '''
    Written assuming only one max and one min per variable.
    cycles is a list of lists of words from {I,D,?}^len(names)
    names is a list of the gene names corresponding to each variable index
    '''
    partialorders = []
    for cyc in cycles:
        extrema = [[]]
        for i,name in enumerate(names):
            ipath = ''.join(c[i] for c in cyc)
            imin,imax = get_min_max(ipath) 
            minblocks = make_consecutive_blocks(imin)
            maxblocks = make_consecutive_blocks(imax)
            if minblocks and maxblocks: (iterator, flag) = (itertools.product(minblocks,maxblocks), 'both')
            else: (iterator,flag) = (minblocks, 'min') or (maxblocks,'max')
            new_extrema = []
            for ex in extrema:
                for block in iterator:
                    new_ex = ex[:]
                    if flag == 'both': new_ex.extend([(name+" min",block[0]),(name+" max",block[1])])
                    else: new_ex.append((name+" "+flag,block))  
                    new_extrema.append(new_ex)
            extrema = new_extrema  
        for ex in extrema:
            intgraph = ig.IntervalGraph(ex)
            graph_dict = { intgraph.vertex_label(v) : tuple([intgraph.vertex_label(w) for w in intgraph.adjacencies(v)]) for v in intgraph.vertices()}
            partialorders.append({'graph' : graph_dict, 'graphviz' : intgraph.graphviz()})
    return partialorders

def extract_edge_paths():
    # need to write function based on paths of the form -m-, ---, M--, etc.
    pass

def make_labeled_cycles(digraph):
    # graph is nx.DiGraph object
    cycles = nx.simple_cycles(digraph)
    cycles = [cyc+[cyc[0]] for cyc in cycles] #first element is left off of the end in simplecycles() output
    labeled_cycles = [[digraph.edge[u][v]["label"] for (u,v) in zip(cyc[:-1],cyc[1:])] for cyc in cycles]
    return labeled_cycles

def make_morse_digraph(paramgraph,paramind,morseset):
    # paramind, morseset are ints (or longs)
    domaingraph = DSGRN.DomainGraph(paramgraph.parameter(paramind))
    searchgraph = DSGRN.SearchGraph(domaingraph)
    morsedecomposition = DSGRN.MorseDecomposition(domaingraph.digraph())
    morseset_of_interest = morsedecomposition.morseset(morseset)
    MR = DSGRN.MatchingRelation(domaingraph.dimension())
    # make networkx digraph in order to find simple cycles
    G = nx.DiGraph()
    G.add_nodes_from(morseset_of_interest)
    edges=[ (i,a) for i in morseset_of_interest for a in domaingraph.digraph().adjacencies(i) if a in morseset_of_interest ]
    edgelabels = { (i,a) : MR.edge_labelstring(searchgraph.event(i,a)) for (i,a) in edges }
    for edge,label in edgelabels.iteritems(): G.add_edge(edge[0],edge[1],label=label)
    return G

# def domain_label(L,D):
#     """
#     Inputs: label L, dimension D
#     Outputs:"label" output L of DomainGraph.label(domain) is converted into a string with "I", "D", and "?"
#     """
#     return ''.join([ "D" if L&(1<<d) else ("I" if L&(1<<(d+D)) else "?") for d in range(0,D) ])

def edge_label(L,D):
    """
    Inputs: label L, dimension D
    Outputs:"label" output L of SearchGraph.event(source,target) is converted into a string with "M", "m", and "-"
    """
    return ''.join([ "M" if L&(1<<d) else ("m" if L&(1<<(d+D)) else "-") for d in range(0,D) ]) 

def iterate_over_params(networkfile="network.txt",FCfile="StableFClist.txt"):
    # network is a DSGRN.Network object
    network = DSGRN.Network(networkfile)
    names = [network.name(i) for i in range(network.size())]
    paramgraph = DSGRN.ParameterGraph(network)
    partialorders = []
    with open(FCfile,'r') as SFC:
        for param_morse in SFC:
            paramind,mset=param_morse.split()
            morse_digraph = make_morse_digraph(paramgraph,long(paramind),int(mset))
            cycles = make_labeled_cycles(morse_digraph)
            partialorders.extend(make_partial_orders(cycles,names))
    return partialorders

def test():
    cyc = ["DDID","?DID","??ID","I?ID","??ID","??DD","?IDD","IIDD","IIDI","DIDI","DIDD","DIID","DDID"]
    extrema=[]
    for i in range(4):
        ipath = ''.join(c[i] for c in cyc)
        imin,imax = get_min_max(ipath)
        extrema.append([imin,imax])
    print extrema == [[[1,2,3],[9]],[[2,3,4,5,6],[12]],[[11],[5]],[[8],[10]]]
    minima = [ [ str(i)+ " min", [e[0][0],e[0][-1] ] ] for i,e in enumerate(extrema)  ]
    maxima = [ [ str(i)+ " max", [e[1][0],e[1][-1] ] ] for i,e in enumerate(extrema)  ]
    extrema = minima + maxima
    graph = ig.IntervalGraph(extrema).transitive_reduction()
    answer = {"0 min":["2 max"],"2 max":["3 min"],"1 min":["3 min"],"3 min":["0 max"],"0 max":["3 max"],"3 max":["2 min"],"2 min":["1 max"],"1 max":[]}
    for v in graph.vertices():
        # print graph.vertex_label(v), [graph.vertex_label(w) for w in  graph.adjacencies(v)]
        print answer[graph.vertex_label(v)] == [graph.vertex_label(w) for w in  graph.adjacencies(v)]
    netdir  = 'testnetworks'
    subprocess.call('mkdir '+netdir,shell=True)
    networkfile = netdir +'/network01.txt'
    # with open(networkfile,'w') as tn:
    #     tn.write('x : ~y : E\ny : x : E')
    # params = {}
    # params['dsgrn'] = '../DSGRN'
    # params['networkfolder'] = netdir
    # params['queryfile'] = 'shellscripts/stableFCqueryscript.sh'
    # params['removeDB'] = 'n'
    # params['removeNF'] = 'n'
    # job = Job('local',params)
    # job.prep()
    # job.run()
    # FCfile = os.path.join(job.DATABASEDIR,'StableFClist01.txt')
    # partialorders = iterate_over_params(networkfile,FCfile)
    # print partialorders == [{'graph': {'x min': (), 'y max': ('x min',), 'y min': ('x min', 'x max', 'y max'), 'x max': ('x min', 'y max')}, 'graphviz': 'digraph {\n0[label="x min"];\n1[label="x max"];\n2[label="y min"];\n3[label="y max"];\n1 -> 0 [label=""];\n1 -> 3 [label=""];\n2 -> 0 [label=""];\n2 -> 1 [label=""];\n2 -> 3 [label=""];\n3 -> 0 [label=""];\n}\n'}, {'graph': {'x min': ('y min',), 'y max': ('x min', 'y min'), 'y min': (), 'x max': ('x min', 'y min', 'y max')}, 'graphviz': 'digraph {\n0[label="x min"];\n1[label="x max"];\n2[label="y min"];\n3[label="y max"];\n0 -> 2 [label=""];\n1 -> 0 [label=""];\n1 -> 2 [label=""];\n1 -> 3 [label=""];\n3 -> 0 [label=""];\n3 -> 2 [label=""];\n}\n'}]
    # # for po in partialorders:
    # #     print po,"\n"
    networkfile = netdir +'/network01.txt'
    with open(networkfile,'w') as tn:
        tn.write('x : (y)(z) : E\ny : ~x : E\nz : y : E')
    params = {}
    params['dsgrn'] = '../DSGRN'
    params['networkfolder'] = netdir
    params['queryfile'] = 'shellscripts/stableFCqueryscript.sh'
    params['removeDB'] = 'n'
    params['removeNF'] = 'n'
    job = Job('local',params)
    job.prep()
    job.run()
    FCfile = os.path.join(job.DATABASEDIR,'StableFClist01.txt')
    network = DSGRN.Network(networkfile)
    names = [network.name(i) for i in range(network.size())]
    paramgraph = DSGRN.ParameterGraph(network)
    with open(FCfile,'r') as SFC:
        for param_morse in SFC:
            paramind,mset=param_morse.split()
            digraph = make_morse_digraph(paramgraph,long(paramind),int(mset))
            cycles = make_labeled_cycles(digraph)
            if int(paramind) == 0:
                setcycles = set([tuple(cyc) for cyc in cycles])
                answer = set([('?I?', '?I?', '??I', 'I??', '?D?', '?DD', 'D?D', '?ID', '?I?'),('?I?', '?I?', '??I', 'I??', '?D?', '?DD', 'D?D', 'D??', '?I?'),('?I?', '?I?', '??I', 'I??', '?D?', '?DD', 'DD?', 'D??', '?I?'),('?I?', '??I', 'I??', '?D?', '?DD', 'D?D', '?ID', 'IID', '?I?'),('?I?', '??I', 'I??', '?D?', '?DD', 'DD?', '?I?'),('?ID', 'IID', 'I??', '?D?', '?DD', 'D?D', '?ID'),('?ID', 'IID', '?DD', 'D?D', '?ID')])
                print setcycles == answer




if __name__ == "__main__":
    test()



    

