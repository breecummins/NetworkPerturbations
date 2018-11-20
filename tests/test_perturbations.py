from NetworkPerturbations.perturbations.makejobs import Job
import NetworkPerturbations.perturbations.graphtranslation as gt
import subprocess,os,json,glob,sys

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


def test_countFP():
    paramfile =  "params_CountFPMatch_X1X2X3.json"
    results, networkspec = run(paramfile)
    assert(len(results)==4)
    assert(networkspec in results)
    assert(results[networkspec]=="8/168")


def test_countFC():
    paramfile = "params_CountStableFC_X1X2X3.json"
    results, networkspec = run(paramfile)
    assert(len(results)==7)
    assert(networkspec in results)
    assert(results[networkspec]=="76/168")
#

def test_patternmatch_stable():
    paramfile = "params_patternmatch_stable_X1X2X3.json"
    results, networkspec = run(paramfile)
    print(results)
    assert(len(results)==4)
    assert(networkspec in results)
    assert(results[networkspec]==[[0.0, 40, 168], [0.1, 54, 168]])

def test_patternmatch_path():
    paramfile = "params_patternmatch_path_domaingraph_X1X2X3.json"
    results, networkspec = run(paramfile)
    print(results)
    assert(len(results)==4)
    assert(networkspec in results)
    assert(results[networkspec]==[[0.0, 58, 168], [0.1, 80, 168]])
