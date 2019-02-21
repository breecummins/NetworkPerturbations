from NetworkPerturbations.perturbations.makejobs import Job
import NetworkPerturbations.perturbations.graphtranslation as gt
import subprocess,os,json,glob

def run(paramfile):
    job = Job(paramfile)
    job.run()
    compdir = subprocess.getoutput("ls -td ./computations*/ | head -1")
    resultsfile = glob.glob(os.path.join(compdir,"results/*"))[0]
    results = json.load(open(resultsfile,'r'))
    subprocess.call("rm -r " + compdir, shell=True)
    netfile = "networkspec_X1X2X3.txt"
    networkspec = open(netfile).read()
    G = gt.getGraphFromNetworkSpec(networkspec)
    networkspec = gt.createEssentialNetworkSpecFromGraph(G)
    return results, networkspec

