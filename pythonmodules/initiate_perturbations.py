import json, sys, subprocess, os, importlib
import pythonmodules.networkperturbations as perturb

params = json.load(open(sys.argv[1]))
query = params["queryfile"]
importlib.import_module(query)

DATETIME = subprocess.check_output(['date +%Y_%m_%d_%H_%M_%S'], shell=True).strip()
compute_path = os.path.join("computations" + DATETIME)
subprocess.call("mkdir -p " + compute_path, shell=True)

# make or retrieve networks
if "networkfolder" in params and params["networkfolder"]:
    for f in os.listdir(params["networkfolder"]):
        networks.append(open(os.path.join(params["networkfolder"],f)).read())
else:
    params["nodelist"] = None
    params["edgelist"] = None
    if "nodefile" in params and params["nodefile"]:
        with open(params["nodefile"]) as nf:
            params["nodelist"] = [l for l in nf]
    if "edgefile" in params and params["edgefile"]:
        with open(params["edgefile"]) as ef:
            params["edgelist"] = [l for l in ef]
    networks = perturb.perturbNetwork(params)

# run query on each network
results = []
for network in networks:
    results.append(query.query(network,compute_path))
json.dump(results,open(os.path.join(compute_path,"results.json"),'w'))

