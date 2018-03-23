import DSGRN, os

networkfile = os.path.expanduser("~/ProjectSimulationResults/wavepool4patternmatch_paper/networks/wavepool09.txt")

network = DSGRN.Network(networkfile)
parametergraph = DSGRN.ParameterGraph(network)
parameter = parametergraph.parameter(3) #parameter 3 has an FC but no pattern matches
domaingraph = DSGRN.DomainGraph(parameter)

def labelstring(L,D):
  """
  Inputs: label L, dimension D
  Outputs:"label" output L of DomainGraph is converted into a string with "I", "D", and "?"
  """
  return ''.join([ "D" if L&(1<<d) else ("I" if L&(1<<(d+D)) else "?") for d in range(0,D) ])

gv = 'digraph {\n'
indices = { k : str(k) for k in range(domaingraph.digraph().size())}
for v in range(domaingraph.digraph().size()): gv += indices[v] + '[label="' + indices[v]+ ': ' + labelstring(domaingraph.label(v),domaingraph.dimension()) + '"];\n'
for v in range(domaingraph.digraph().size()):
    for u in domaingraph.digraph().adjacencies(v): 
        gv += indices[v] + ' -> ' + indices[u] + ';\n'
gv += '}'

with open(os.path.expanduser('~/ProjectSimulationResults/wavepool4patternmatch_paper/wavepool09_domaingraph.gv'),'w') as f:
    f.write(gv)

morsedecomposition = DSGRN.MorseDecomposition(domaingraph.digraph())
print([ len(morsedecomposition.morseset(i)) for i in range(0,morsedecomposition.poset().size()) ])