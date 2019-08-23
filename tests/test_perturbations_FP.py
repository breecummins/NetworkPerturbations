from run_tests import run

netfile = "networkspec_X1X2X3.txt"

def test_countFP():
    paramfile =  "params_CountFPMatch_X1X2X3.json"
    results, networkspec = run(paramfile,netfile)
    assert(len(results)==3)
    assert(networkspec in results)
    assert(results[networkspec]==[8,168])

def test_countFP_anon():
    paramfile =  "params_anonadds_CountFPMatch_X1X2X3.json"
    results, networkspec = run(paramfile,netfile)
    assert(len(results)==3)
    assert(networkspec in results)
    assert(results[networkspec]==[8,168])
    results2, networkspec = run(paramfile,netfile)
    assert (results == results2)

def test_countFP_remove():
    paramfile =  "params_remove_CountFPMatch_X1X2X3.json"
    results, networkspec = run(paramfile,netfile)
    assert(len(results)==6)
    assert(networkspec in results)
    assert(results[networkspec]==[8,168])

def test_countFP_remove_with_filter():
    paramfile =  "params_remove_CountFPMatch_with_filter_X1X2X3.json"
    results, networkspec = run(paramfile,netfile)
    print(results)
    assert(len(results)==6)
    assert(networkspec in results)
    assert(results[networkspec]==[8,168])
    assert(results=={'X1 : (X1)(~X3) : E\nX2 : (X1) : E\nX3 : (X2) : E\n': [4, 14], 'X1 : (X1)(~X3) : E\nX2 : (X1) : E\nX3 : (X1 + X2 + x4) : E\nx4 : (X1) : E\n': [120, 4968], 'X1 : (X1)(~X3) : E\nX2 : (X1) : E\nX3 : (X1 + X2) : E\n': [8, 168], 'X1 : (X1 + X3) : E\nX2 : (X1) : E\nX3 : (X1 + X2) : E\n': [24, 168], 'X1 : (X1)(~X3) : E\nX2 : (X3) : E\nX3 : (X1 + X2 + x4) : E\nx4 : (~X2) : E\n': [0, 4872], 'X1 : (X1)(~X3) : E\nX2 : (X1)(~X3) : E\nX3 : (X1 + X2) : E\n': [48, 2352]})


if __name__ == "__main__":
    test_countFP_remove_with_filter()