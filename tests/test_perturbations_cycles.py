from run_tests import run

netfile = "networkspec_X1X2X3.txt"

def test_countFC():
    paramfile = "params_CountStableFC_X1X2X3.json"
    results, networkspec = run(paramfile,netfile)
    assert(len(results)==3)
    assert(networkspec in results)
    assert(results[networkspec]=="76/168")
