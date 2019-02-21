from run_tests import run

def test_patternmatch_stable():
    paramfile = "params_patternmatch_stable_X1X2X3.json"
    results, networkspec = run(paramfile)
    print(results)
    assert(len(results)==3)
    assert(networkspec in results)
    assert(results[networkspec]==[[0.0, 40, 168], [0.1, 54, 168]])

def test_patternmatch_path():
    paramfile = "params_patternmatch_path_domaingraph_X1X2X3.json"
    results, networkspec = run(paramfile)
    print(results)
    assert(len(results)==3)
    assert(networkspec in results)
    assert(results[networkspec]==[[0.0, 58, 168], [0.1, 80, 168]])
