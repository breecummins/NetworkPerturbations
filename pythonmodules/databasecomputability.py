import DSGRN

def checkComputability(network_spec,maxparams):
    network=DSGRN.Network()
    network.assign(network_spec)
    try:
        paramgraph=DSGRN.ParameterGraph(network)    
        return (paramgraph.size() <= int(maxparams))
    except:
        return False