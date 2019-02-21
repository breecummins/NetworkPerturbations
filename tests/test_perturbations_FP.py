from run_tests import run

def test_countFP():
    paramfile =  "params_CountFPMatch_X1X2X3.json"
    results, networkspec = run(paramfile)
    assert(len(results)==3)
    assert(networkspec in results)
    assert(results[networkspec]=="8/168")

def test_countFP_anon():
    paramfile =  "params_anonadds_CountFPMatch_X1X2X3.json"
    results, networkspec = run(paramfile)
    assert(len(results)==3)
    assert(networkspec in results)
    assert(results[networkspec]=="8/168")
    results2, networkspec = run(paramfile)
    assert (results == results2)

def test_countFP_remove():
    paramfile =  "params_remove_CountFPMatch_X1X2X3.json"
    results, networkspec = run(paramfile)
    assert(len(results)==6)
    assert(networkspec in results)
    assert(results[networkspec]=="8/168")

