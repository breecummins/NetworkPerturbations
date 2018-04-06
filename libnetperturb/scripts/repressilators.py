import DSGRN
import time
import topsort

#FIXME: port to new DSGRN, new triplet merge tree code, and Python 3

def hasMatch(events,event_ordering,networkspec):
    network = DSGRN.Network()
    network.assign(networkspec)
    poe = DSGRN.PosetOfExtrema(network,events,event_ordering)
    patterngraph = DSGRN.PatternGraph(poe)
    paramgraph = DSGRN.ParameterGraph(network)
    for paramind in range(paramgraph.size()):
        domaingraph = DSGRN.DomainGraph(paramgraph.parameter(paramind))
        morsedecomposition = DSGRN.MorseDecomposition(domaingraph.digraph())
        morsegraph = DSGRN.MorseGraph()
        morsegraph.assign(domaingraph,morsedecomposition)
        for i in range(0,morsedecomposition.poset().size()):
            ms = morsedecomposition.morseset(i)
            if morsegraph.annotation(i)[0] == "FC" and len(morsedecomposition.poset().children(i)) == 0:
                searchgraph = DSGRN.SearchGraph(domaingraph,i)
                matchinggraph = DSGRN.MatchingGraph(searchgraph,patterngraph)
                if DSGRN.QueryCycleMatch(matchinggraph): 
                    return True
                else:
                    continue
    return False

def checkLinearExtensionsOfPoset(netspec,events,event_ordering):
    # the poset event_ordering is required to be indexed such that every edge (i,j) satisfies i < j
    # also, indexing starts at 1
    poset = [(a+1,b+1) for (a,b) in event_ordering]
    N = len(events)
    grid = topsort.partial_order_to_grid(poset,N)
    all_matches = True
    # j=0
    for l in topsort.vr_topsort(N, grid):
        l = [ k-1 for k in l] # -1 to get back to zero indexing
        linext = [(l[i],l[i+1]) for i in range(N-1)] 
        if not hasMatch(events,linext,netspec):
            all_matches = False
            print(l)
            break
        # j += 1
        # if not j%1000: print(j)
    return "Has all linear extensions of known order = {}".format(all_matches)

def doubleRepressilatorOrders(netspec):
    events = [("x1","max"),("y1","min"),("z1","max"),("x1","min"),("y1","max"),("z1","min"),
              ("x2","max"),("y2","min"),("z2","max"),("x2","min"),("y2","max"),("z2","min")]
    event_ordering_known = [(0,1),(1,2),(2,3),(3,4),(4,5)] + [(6,7),(7,8),(8,9),(9,10),(10,11)]
    event_ordering_mixedup = [(0,1),(1,2),(2,3),(3,4),(4,5)] + [(7,6),(6,8),(8,10),(10,9),(9,11)]
    event_ordering_oppositemix = [(1,0),(0,2),(2,4),(4,3),(3,5)] + [(6,7),(7,8),(8,9),(9,10),(10,11)]
    print("Matches known order = {}".format(hasMatch(events,event_ordering_known,netspec)))
    print("Matches mixed up order = {}".format(hasMatch(events,event_ordering_mixedup,netspec)))
    print("Matches opposite mixed up order = {}".format(hasMatch(events,event_ordering_oppositemix,netspec)))
    print(checkLinearExtensions(netspec,events,event_ordering_known))

def singleRepressilator():
    print("\nSingle repressilator")
    netspec = "x1 : ~z1 : E\ny1 : ~x1 : E\nz1 : ~y1 : E"
    events = [("x1","max"),("y1","min"),("z1","max"),("x1","min"),("y1","max"),("z1","min")]
    event_ordering_known = [(0,1),(1,2),(2,3),(3,4),(4,5)]
    event_ordering_mixedup = [(1,0),(0,2),(2,4),(4,3),(3,5)]
    print("Matches known order = {}".format(hasMatch(events,event_ordering_known,netspec)))
    print("Matches mixed up order = {}".format(hasMatch(events,event_ordering_mixedup,netspec)))

def decoupledRepressilators():
    print("\nDecoupled repressilators")
    netspec = "x1 : ~z1 : E\ny1 : ~x1 : E\nz1 : ~y1 : E\nx2 : ~z2 : E\ny2 : ~x2 : E\nz2 : ~y2 : E"
    doubleRepressilatorOrders(netspec)

def oneWayForcing():
    print("\nOne-way forcing")
    netspec = "x1 : ~z1 : E\ny1 : ~x1 : E\nz1 : ~y1 : E\nx2 : ~z2 : E\ny2 : (~x1)(~x2) : E\nz2 : ~y2 : E"
    doubleRepressilatorOrders(netspec)

def twoWayFeedback():
    print("\nTwo-way feedback")
    netspec = "x1 : ~z1 : E\ny1 : (~x1)(~x2) : E\nz1 : ~y1 : E\nx2 : ~z2 : E\ny2 : (~x1)(~x2) : E\nz2 : ~y2 : E"
    doubleRepressilatorOrders(netspec)

def sharedNode():
    netspec = "x1 : ~z1 : E\ny : (~x1)(~x2) : E\nz1 : ~y : E\nx2 : ~z2 : E\nz2 : ~y : E"
    
def isOneWaySubsetTwoWay():
    netspec_oneway = "x1 : ~z1 : E\ny1 : ~x1 : E\nz1 : ~y1 : E\nx2 : ~z2 : E\ny2 : (~x1)(~x2) : E\nz2 : ~y2 : E"
    netspec_twoway = "x1 : ~z1 : E\ny1 : (~x1)(~x2) : E\nz1 : ~y1 : E\nx2 : ~z2 : E\ny2 : (~x1)(~x2) : E\nz2 : ~y2 : E"
    events = [("x1","max"),("y1","min"),("z1","max"),("x1","min"),("y1","max"),("z1","min"),
              ("x2","max"),("y2","min"),("z2","max"),("x2","min"),("y2","max"),("z2","min")]
    N = len(events)-1
    # make all permutations of the last n-1 elements in events (this gets rid of cyclic permutations of all elements)
    # this method is much faster than using itertools.permutations(1,N+1)
    grid = topsort.partial_order_to_grid([],N)
    all_matches = True
    j = 0
    start=time.clock()
    for l in topsort.vr_topsort(N, grid):
        l = [0]+list(l) # adding 0 on the front ensures that we have no cyclic permutations in order of events
        linext = [(l[i],l[i+1]) for i in range(N)] 
        if hasMatch(events,linext,netspec_oneway) and not hasMatch(events,linext,netspec_twoway): 
            print(l)
            all_matches=False
            break
        j += 1
        if not j%100000: 
            print((j, time.clock()-start))
    print("One-way forcing subset of two-way forcing = {}".format(all_matches))

if __name__ == "__main__":
    # singleRepressilator()
    # decoupledRepressilators()
    # oneWayForcing()
    # twoWayFeedback()
    # sharedNode()

    isOneWaySubsetTwoWay()