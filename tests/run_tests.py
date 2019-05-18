from NetworkPerturbations.perturbations.makejobs import Job
import NetworkPerturbations.perturbations.graphtranslation as gt
import subprocess,os,json

def run(paramfile,netfile):
    job = Job(paramfile)
    job.run()
    qdir = subprocess.getoutput("ls -td ./queries*/ | head -1")
    resultsfile = os.path.join(qdir,"query_results.json")
    results = json.load(open(resultsfile,'r'))
    # subprocess.call("rm -r " + qdir, shell=True)
    # subprocess.call("rm -r " + subprocess.getoutput("ls -td ./perturbations*/ | head -1"), shell=True)
    # subprocess.call("rm -r " + subprocess.getoutput("ls -td ./inputs*/ | head -1"), shell=True)
    networkspec = open(netfile).read()
    G = gt.getGraphFromNetworkSpec(networkspec)
    networkspec = gt.createEssentialNetworkSpecFromGraph(G)
    return results, networkspec

