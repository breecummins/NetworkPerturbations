import DSGRN
import itertools

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


if __name__ == "__main__":
    import sys

    # single repressilator
    netspec0 = "x1 : ~z1 : E\ny1 : ~x1 : E\nz1 : ~y1 : E"
    # decoupled repressilators
    netspec1 = "x1 : ~z1 : E\ny1 : ~x1 : E\nz1 : ~y1 : E\nx2 : ~z2 : E\ny2 : ~x2 : E\nz2 : ~y2 : E"
    # one-way forcing
    netspec2 = "x1 : ~z1 : E\ny1 : ~x1 : E\nz1 : ~y1 : E\nx2 : ~z2 : E\ny2 : (~x1)(~x2) : E\nz2 : ~y2 : E"
    # two-way feedback
    netspec3 = "x1 : ~z1 : E\ny1 : (~x1)(~x2) : E\nz1 : ~y1 : E\nx2 : ~z2 : E\ny2 : (~x1)(~x2) : E\nz2 : ~y2 : E"
    # shared node
    netspec4 = "x1 : ~z1 : E\ny : (~x1)(~x2) : E\nz1 : ~y : E\nx2 : ~z2 : E\nz2 : ~y : E"
    # non-repressilator example
    netspec5 = "X : (~Z)(Y) : E\nY : ~X : E\nZ : ~Y : E"

    events0 = [("x1","min"),("x1","max"),("y1","min"),("y1","max"),("z1","min"),("z1","max")]
    event_ordering0 = [(1,2),(2,5),(5,0),(0,3),(3,4)]
    # event_ordering0 = [(1,2),(2,0),(0,3)]
    # event_ordering0 = [(2,5),(5,3),(3,4)]

    events1 = events0 + [("x2","min"),("x2","max"),("y2","min"),("y2","max"),("z2","min"),("z2","max")]
    event_ordering1 = event_ordering0 + [(7,8),(8,11),(11,6),(6,9),(9,10)]
    # event_ordering1 = [(7,0),(0,8),(8,3),(3,11),(11,4),(4,6),(6,1),(1,9),(9,2),(2,10),(10,5)]
    # event_ordering1 = [(7,11),(11,9),(9,6),(6,10),(10,8)]
    # event_ordering3 = [(7,8),(8,11),(11,6),(6,9),(9,10)]

    num = sys.argv[1]
    ns = eval("netspec" + num)
    ev = eval("events"+num)
    evo = eval("event_ordering"+num)
    print "\n" + ns + "\n\n"
    sys.stdout.flush()

    print hasMatch(ev,evo,networkspec=ns)

    # cycles = []
    # cycle_perms = set([])
    # for p in itertools.permutations(range(6,12)):
    #     cycle_perms.update([ p[n:] + p[:n] for n in range(1,len(p)) ])
    #     if p not in cycle_perms:
    #         cycles.append(p)
    # print len(cycles)
    # for p in cycles:
    #     evo = tuple([(p[i],p[i+1]) for i in range(len(p)-1)])
    #     if isMatch(ev,evo,networkspec=ns):
    #         print evo
