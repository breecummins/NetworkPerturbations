import sys,json

network_spec_file=sys.argv[1]
pattern_spec_file=sys.argv[2]
results_file=sys.argv[3]
results_dict=dict(eval(sys.argv[4]))
nummatches=sys.argv[5]

if nummatches:
	results_dict["StableFCMatchesParameterCount"] = int(nummatches)

with open(network_spec_file,'r') as nf:
    networkstr = nf.read()

results_dict["Network"]=networkstr

if pattern_spec_file:
    with open(pattern_spec_file,'r') as pf:
        patstr = json.load(pf)
else:
    patstr = "None"

results_dict["PatternSpecification"]=patstr

json.dump(results_dict,open(results_file,'w'))
