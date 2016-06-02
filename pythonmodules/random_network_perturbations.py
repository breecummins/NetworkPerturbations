import fileparsers
from databasecomputability import checkComputability
import random,sys

def getRandomInt(n):
    return random.randrange(n)

def addEdge(graph,reg):
    n = len(graph)
    startnode = getRandomInt(n)
    endnode = getRandomInt(n)
    while endnode == startnode and endnode in graph[startnode]:
        # exclude existing activating self-loops (can't switch sign)
        startnode = getRandomInt(n)
        endnode = getRandomInt(n)
    if endnode == startnode:
        # add self-activation only (no self-repression allowed)
        graph[startnode].append(endnode)
        reg[startnode].append('a')
    elif endnode in graph[startnode]:
        # swap regulation if edge already exists
        ind = graph[startnode].index(endnode)
        thisreg = reg[startnode][ind]
        reg[startnode][ind] = 'a'*(thisreg == 'r') + 'r'*(thisreg == 'a')
    else:
        # otherwise add edge with random sign
        graph[startnode].append(endnode)
        regbool = getRandomInt(2)
        reg[startnode].append('a'*regbool + 'r'*(not regbool))
    return graph, reg

def addNode(graph,reg):
    n = len(graph)
    # the new node will have index n
    # pick an incoming edge for n from the existing network (i.e. don't pick node n)
    innode = getRandomInt(n) # NOT getRandomInt(n+1)
    inreg = getRandomInt(2)
    graph[innode].append(n)
    reg[innode].append('a'*inreg + 'r'*(not inreg))
    # pick an outgoing edge for n from the existing network
    outnode = getRandomInt(n)
    outreg = getRandomInt(2)
    graph.append([outnode])
    reg.append(['a'*outreg + 'r'*(not outreg)])
    return graph, reg

def perturbNetwork(graph,reg):
    keepgoing = 1
    while keepgoing:
        edge = getRandomInt(2)
        if edge:
            graph,reg = addEdge(graph,reg)
        else:
            graph,reg = addNode(graph,reg)
        keepgoing = getRandomInt(2)
    return graph,reg

def makeNearbyNetworks(starting_network_filename,numperturbations,savename = 'network_',maxparams=200000):
    # reset random seed for every run
    random.seed()
    # generate starting graph of labeled out-edges (activation and repression)
    node_list,starting_graph,starting_regulation,_ = fileparsers.getGraphFromNetworkFile(network_filename=starting_network_filename)
    # begin analysis with starting network spec -- change var names, save to file, and initialize networks with [networkstr]
    # node_list = ['x'+str(k) for k in range(len(starting_graph))]
    essential = [True] * len(starting_graph)
    fname = savename+str(0)+'.txt'  
    networks = [fileparsers.createNetworkFile(node_list,starting_graph,starting_regulation,essential,fname=fname,save2file=True)]
    # now make perturbations
    # note that the while loop below can be an infinite loop if numperturbations is too large for maxnodes and maxparams
    while len(networks) < int(numperturbations)+1: 
        # below: the lists within the starting graph must be explicitly copied or else the starting graph gets reassigned within perturbNetwork
        sg = [list(outedges) for outedges in starting_graph]  
        sr = [list(reg) for reg in starting_regulation]
        # perturb the starting network
        graph,reg = perturbNetwork(sg,sr)
        # extract the network spec from the graph and regulation type
        # node_list = ['x'+str(k) for k in range(len(graph))]
        new_node_list = node_list + ['x'+str(k) for k in range(len(graph)-len(node_list))]
        essential = [True] * len(graph)
        network_spec = fileparsers.createNetworkFile(new_node_list,graph,reg,essential,save2file=False)
        # check that network spec is all of unique, small enough, and computable, then write to file and save string for comparison
        if (network_spec not in networks) and checkComputability(network_spec,maxparams):
            fname = savename+str(len(networks))+'.txt'
            with open(fname,'w') as f:
                f.write(network_spec)
            networks.append(network_spec)

if __name__ == '__main__':
    # fname="/Users/bcummins/GIT/DSGRN/networks/5D_2016_02_08_cancer_withRP_essential.txt"
    # numperturbations = 200
    # savename = 'networks/network_'
    makeNearbyNetworks(*sys.argv[1:])

