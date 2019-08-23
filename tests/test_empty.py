from run_tests import run
import time

netfile = "empty_network.txt"

def test_patternmatch():
    paramfile = "params_empty.json"
    results, networkspec = run(paramfile,netfile,"query_results_PathMatchInDomainGraph.json")
    print(results)
    assert(len(results)==0)
    time.sleep(1)

def test_patternmatch2():
    paramfile = "params_empty2.json"
    results, networkspec = run(paramfile,netfile,"query_results_PathMatchInDomainGraph.json")
    print(results)
    assert(len(results)==3)

