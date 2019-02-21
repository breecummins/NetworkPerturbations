from run_tests import run

def test_countFC():
    paramfile = "params_CountStableFC_X1X2X3.json"
    results, networkspec = run(paramfile)
    assert(len(results)==3)
    assert(networkspec in results)
    assert(results[networkspec]=="76/168")

