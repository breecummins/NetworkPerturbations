from run_tests import run
import warnings

netfile = "networkspec_X1X2X3.txt"

def test_patternmatch_stable():
    paramfile = "params_patternmatch_stable_X1X2X3.json"
    results, networkspec = run(paramfile,netfile,"query_results_CycleMatchInStableMorseSet.json")
    print(results)
    assert(len(results)==3)
    assert(networkspec in results)
    assert(results=={'X1 : (X1)(~X3) : E\nX2 : (X1 + X3) : E\nX3 : (X1 + X2) : E\n': [[0.0, 205, 2352], [0.1, 317, 2352]], 'X1 : (X1)(~X3) : E\nX2 : (X1) : E\nX3 : (X1 + X2) : E\n': [[0.0, 40, 168], [0.1, 54, 168]], 'X1 : (X1)(~X3) : E\nX2 : (X3)(~X1) : E\nX3 : (X1 + X2) : E\n': [[0.0, 0, 2352], [0.1, 0, 2352]]})

def test_patternmatch_path():
    paramfile = "params_patternmatch_path_domaingraph_X1X2X3.json"
    results, networkspec = run(paramfile,netfile,"query_results_PathMatchInDomainGraph.json")
    print(results)
    assert(len(results)==3)
    assert(networkspec in results)
    assert(results[networkspec]==[[0.0, 58, 168], [0.1, 80, 168]])

def test_patternmatch_path_wavepool():
    paramfile = "params_patternmatch_path_domaingraph_wavepool.json"
    results, networkspec = run(paramfile,"good_wavepool.txt","query_results_PathMatchInDomainGraph.json")
    print(networkspec)
    print(results)
    assert(results=={'SWI4 : (NDD1)(~YOX1) : E\nHCM1 : SWI4 : E\nNDD1 : HCM1 : E\nYOX1 : SWI4 : E': [[0.0, 0, 14], [0.01, 8, 14], [0.05, 5, 14]]})
    results, networkspec = run(paramfile,"good_wavepool.txt","query_results_PathMatchInStableFullCycle.json")
    print(networkspec)
    print(results)
    assert(results=={'SWI4 : (NDD1)(~YOX1) : E\nHCM1 : SWI4 : E\nNDD1 : HCM1 : E\nYOX1 : SWI4 : E': [[0.0, 0, 14], [0.01, 2, 14], [0.05, 1, 14]]})

def test_patternmatch_path_badwavepool():
    paramfile = "params_patternmatch_path_domaingraph_badwavepool.json"
    with warnings.catch_warnings(record=True) as w:
        # Trigger a warning.
        _ = run(paramfile,"bad_wavepool.txt","query_results_PathMatchInDomainGraph.json")
        # Verify some things
        print(w)
        assert(len(w) == 0)

if __name__ == "__main__":
    test_patternmatch_path_wavepool()