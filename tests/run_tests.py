from NetworkPerturbations.perturbations.makejobs import Job
import NetworkPerturbations.perturbations.graphtranslation as gt
import subprocess,os,json

def run(paramfile,netfile,queryfile="query_results.json"):
    job = Job(paramfile)
    job.run()
    qdir = subprocess.getoutput("ls -td ./computations*/queries*/ | head -1")
    if isinstance(queryfile,str):
        resultsfile = os.path.join(qdir, queryfile)
        results=json.load(open(resultsfile,'r'))
    else:
        results = []
        for qf in queryfile:
            resultsfile = os.path.join(qdir, qf)
            results.append(json.load(open(resultsfile,'r')))
    subprocess.call("rm -r " + qdir, shell=True)
    subprocess.call("rm -r " + subprocess.getoutput("ls -td ./computations*/ | head -1"), shell=True)
    networkspec = open(netfile).read()
    G = gt.getGraphFromNetworkSpec(networkspec)
    networkspec = gt.createEssentialNetworkSpecFromGraph(G)
    return results, networkspec

