import DSGRN

# waiting on feature request from Shaun to take network spec instead of file

def checkComputability(network_spec,maxparams):
    try:
        paramgraph=DSGRN.ParameterGraph(DSGRN.Network(network_spec))    
        return (paramgraph.size() <= int(maxparams))
    except:
        return False