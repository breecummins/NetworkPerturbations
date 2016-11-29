import DSGRN
import subprocess
import graphviz


with open('testnetwork.txt','w') as f:
    f.write('S : (S) \nMD : (S) : E\nRp : (~MD) : E\nEE : (MD + EE)(~Rp) : E')

# subprocess.call('mpiexec -np 4 ../DSGRN/software/Signatures/bin/Signatures testnetwork.txt testnetwork.db',shell=True)

FP_OFF= {"EE":[0,0],"Rp":[1,1]}
FP_ON={"EE":[1,8],"Rp":[0,0]}


database = DSGRN.Database('testnetwork.db')
Q = DSGRN.MonostableFixedPointQuery(database, FP_OFF).matches()
P = DSGRN.MonostableFixedPointQuery(database, FP_ON).matches()
B = DSGRN.DoubleFixedPointQuery(database, FP_OFF, FP_ON).matches()
single_gene_query = DSGRN.SingleGeneQuery(database, "S")
QQ = DSGRN.SingleFixedPointQuery(database, FP_OFF).matches()
PP = DSGRN.SingleFixedPointQuery(database, FP_ON).matches()

for n in range(single_gene_query.number_of_reduced_parameters()):
    graph = single_gene_query(n)
    graph.color = lambda v : "green" if graph.mgi(v) in Q else ("red" if graph.mgi(v) in P else ( "yellow" if graph.mgi(v) in B else ("darkgreen" if graph.mgi(v) in QQ else ("orange" if graph.mgi(v) in PP else "white"))))
    graphstr = 'digraph {' + \
  '\n'.join([ 'X' + str(v) + '[label="' + graph.label(v) + '";style="filled";fillcolor="' + graph.color(v) + '"];' for v in graph.vertices ]) + \
   '\n' + '\n'.join([ 'X' + str(u) + " -> " + 'X' + str(v) + ';' for (u, v) in graph.edges ]) + \
   '\n' + '}\n'
    with open("testgraph{:02d}.gv".format(n),"w") as f:
        f.write(graphstr)
    # for v in graph.vertices:
    #     if graph.color(v) == "white":
    #         parametergraph = DSGRN.ParameterGraph(DSGRN.Network('testnetwork.txt'))
    #         parameter = parametergraph.parameter(single_gene_query.database.full_parameter_index(n,v,database.network.index("S")))
    #         domaingraph = DSGRN.DomainGraph(parameter)
    #         morsedecomposition = DSGRN.MorseDecomposition(domaingraph.digraph())
    #         morsegraph = DSGRN.MorseGraph()
    #         morsegraph.assign(domaingraph, morsedecomposition)
    #         break
    # if n == 10:
    #     for v in graph.vertices:
    #         parametergraph = DSGRN.ParameterGraph(DSGRN.Network('testnetwork.txt'))
    #         parameter = parametergraph.parameter(single_gene_query.database.full_parameter_index(n,v,database.network.index("S")))
    #         domaingraph = DSGRN.DomainGraph(parameter)
    #         morsedecomposition = DSGRN.MorseDecomposition(domaingraph.digraph())
    #         morsegraph = DSGRN.MorseGraph()
    #         morsegraph.assign(domaingraph, morsedecomposition)
    #         with open("testmorsegraph{:02d}_{:02d}.gv".format(n,v),"w") as f:
    #             f.write(morsegraph.graphviz())
    # with open("testmorsegraph{:02d}.gv".format(n),"w") as f:
    #     f.write(morsegraph.graphviz())



