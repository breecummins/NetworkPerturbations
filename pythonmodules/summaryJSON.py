import sys,json

network_spec_file=sys.argv[1]
pattern_spec_file=sys.argv[2]
results_file=sys.argv[3]
summary_str=sys.argv[4]
nummatches=sys.argv[5]

results_dict = dict()

with open(network_spec_file,'r') as nf:
    networkstr = nf.read()
results_dict["Network"]=networkstr

if pattern_spec_file:
    with open(pattern_spec_file,'r') as pf:
        pattern = json.load(pf)
    results_dict["PatternSpecification"]=pattern

for pair in summary_str.split():
    name, val = pair.split(':', 1)
    try: val = eval(val)
    except: pass
    results_dict[name]=val

if nummatches:
	results_dict["StableFCMatchesParameterCount"] = int(nummatches)

json.dump(results_dict,open(results_file,'w'))
