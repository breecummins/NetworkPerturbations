import DSGRN

def query(networks,resultsdir):
    for net in networks:
        network = DSGRN.Network()
        network.assign(net)

