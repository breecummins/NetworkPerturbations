import DSGRN
import queryDSGRN
import itertools

# Order of variables in network file: S, MD, Rp, EE
# Then low FP is [*,*,1,0]
# high FP is [*,*,0,>0]

networkfile = 'Yaonetworks_nonessential/network32.txt'
dbfile = 'Yaonetworks_nonessential_databases/database32.db'

def getAnnotations(param):
    domaingraph = DSGRN.DomainGraph(param)
    morsedecomposition = DSGRN.MorseDecomposition(domaingraph.digraph())
    morsegraph = DSGRN.MorseGraph()
    morsegraph.assign(domaingraph, morsedecomposition)
    mg = eval(morsegraph.stringify())
    return list(itertools.chain(*mg['annotations']))

def Yao_FPs(param):
    hexcode = param.logic()[0].hex()
    ann = getAnnotations(param)
    nums = [tuple([int(i) for i in a if i.isdigit()][-2:]) for a in ann if a[:2]=='FP']
    low_cond = (1,0) in nums
    high_cond = any(filter(lambda x: x[0] ==0 and x[1] > 0,nums))
    if hexcode == '0':
        Sparam = 'off'
        condition = low_cond and not high_cond
    elif hexcode == 'F':
        Sparam = 'on'
        condition = high_cond and not low_cond
    else:
        Sparam = 'middle'
        condition = low_cond and high_cond
    return Sparam, condition

def fullinducibility_usingDSGRN():
    network = DSGRN.Network(networkfile)
    print open(networkfile).read()
    parametergraph = DSGRN.ParameterGraph(network)
    num_factor_graphs = parametergraph.size() / 6 # There are 6 S parameters, disregarding order parameter
    OFF, ON, BiStab = set([]),set([]),set([])
    for p in xrange(parametergraph.size()):
        param = parametergraph.parameter(p)
        Sparam,condition = Yao_FPs(param)
        factor_param = tuple([ tuple([ tuple(a) for a in v  ]) for v in eval(param.stringify())[1:]]) #[1:] means cut off S param, use tuples for set intersection (could use reduced parameter index here, but I don't know how to calculate it)
        if not condition: pass
        elif Sparam == 'off': OFF.add(factor_param)
        elif Sparam == 'on': ON.add(factor_param) 
        else: BiStab.add(factor_param)
    display(OFF,ON,BiStab,num_factor_graphs)

def fullinducibility_usingqueryDSGRN():
    database = queryDSGRN.dsgrnDatabase(dbfile)
    print(database.network.specification())    
    size_factor_graph,num_factor_graphs = database.single_gene_query_prepare("S")
    FP_OFF= {"EE":[0,0],"Rp":[1,1]}
    FP_ON={"EE":[1,8],"Rp":[0,0]}
    matchesBiStab = frozenset(database.DoubleFPQuery(FP_ON,FP_OFF))
    matchesOFF = frozenset(set(database.SingleFPQuery(FP_OFF)).difference(matchesBiStab))
    matchesON = frozenset(set(database.SingleFPQuery(FP_ON)).difference(matchesBiStab))
    min_gpi = 0
    max_gpi = size_factor_graph-1
    OFF, ON, BiStab = set([]),set([]),set([])
    for m in range(num_factor_graphs):
        graph = database.single_gene_query("S", m)
        if graph.mgi(min_gpi) in matchesOFF: OFF.add(m)
        if graph.mgi(max_gpi) in matchesON: ON.add(m)
        for i in range(min_gpi+1,max_gpi):
            if graph.mgi(i) in matchesBiStab:
                BiStab.add(m)
                break
    display(OFF,ON,BiStab,num_factor_graphs)

def display(OFF,ON,BiStab,num_factor_graphs):
    resettablebistability = BiStab.intersection(OFF)
    inducibility = BiStab.intersection(ON)
    fullinducibility = resettablebistability.intersection(inducibility)
    print "Resettable bistability in {} of {} factor graphs.".format(len(resettablebistability),num_factor_graphs)
    print "Inducibility in {} of {} factor graphs.".format(len(inducibility),num_factor_graphs)
    print "Full inducibility in {} of {} factor graphs.".format(len(fullinducibility),num_factor_graphs)
   
if __name__ == '__main__':
    print "\nUsing DSGRN:\n"
    fullinducibility_usingDSGRN()
    print "\nUsing queryDSGRN:\n"
    fullinducibility_usingqueryDSGRN()
