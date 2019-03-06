# Getting started

This module accepts a network in DSGRN network specification format, generates a collection of networks in the neighborhood of the first, perhaps constrained by certain nodes and edges, and performs a DSGRN query on every parameter of every network.

__Dependencies:__ Python 3.6/3.7, numpy, networkx, multiprocessing, pandas, DSGRN (https://github.com/shaunharker/DSGRN) and dependencies, and min_interval_posets (https://github.com/breecummins/min_interval_posets).

To install, do
    
    cd NetworkPerturbations
    . install.sh

To run tests to confirm the code is working as expected, do

    cd tests
    pytest

Calling script is `scripts/call_job.py`:

    python call_job.py <params.json>
    

See the parameter files in the `tests` folder for examples of the input argument to `call_jobs.py`. The keywords in the json parameter dictionary are given as follows.

# Parameters 
__Required:__

    networkfile         =   path to a file containing either a single network specification
                            or a list of them (comma-separated and surrounded by square
                            brackets, saved as plain text)

    makeperturbations   =   true or false (must be lowercase, no quotes);
                            false = perform the query only for the network specifications 
                                    provided in the list;
                            true = for every network spec in the list, make perturbations using 
                                   the optional parameters listed farther down
                                   
If a DSGRN query is desired, with or without perturbations, the following arguments are required:
    
    querymodule     =   module name from 'queries' folder that has the query to be performed
    
    querymodule_args    =   dictionary containing query module specific arguments -- see 
                            individual query documentation. Can be empty for some queries.

The user may optionally specify a location where the results folder will be generated.

    computationsdir     =   path to location where results are to be stored; 
                            default is current directory



If `makeperturbations` is true, the following are optional parameters with the defaults listed:

    probabilities      =   dictionary with operations keying the probability that the operation will occur
                           default = 
                           {"addNode" : 0.50, "removeNode" : 0.0, "addEdge" : 0.50, "removeEdge" : 0.0}
                                               
    range_operations   =   [int,int] min to max # of node/edge changes allowed per graph, endpoint inclusive
                           default = [1,10]

    numperturbations    =   Maximum number of perturbed networks to find (integer);
                            process may time out before this number is reached
                            default = 1000

    maxparams           =   Maximum number of parameters (integer) allowed for DSGRN computations
                            default = 100000

    time_to_wait        =   Maximum time in seconds (integer) allowed to calculate perturbed networks;
                            intended as a fail-safe when there are not enough computable networks 
                            in the neighborhood
                            default = 30

    nodefile            =   path to file containing the names of nodes to add, one line per name;
                            or empty string "" or missing keyword if no such file exists
                            default = no file

    edgefile            =   path to file containing named edges to add, one per line,
                            in the form TARGET_NODE = TYPE_REG(SOURCE_NODE),
                            where TYPE_REG  is a (activation) or r (repression);
                            or empty string "" or missing keyword if no such file exists
                            default = no file

    filters             =   dictionary of function names keying dictionaries with keyword arguments
                            format: 
                            {"function_name1" : kwargs_dict_1, "function_name2" : kwargs_dict_2, ... }
                            See filters.py for the implemented filter functions and their arguments.
                            default = no filters
                        
    compressed_output   =   (true or false) prints count of warnings instead of printing every network spec 
                            that fails filtering. This should only be set to false for trouble-shooting.
                            default = true
                            
    DSGRN_optimized     =   (true or false) prioritizes adding new edges to nodes missing in- or out-edges.
                            Should only be set to false if nodes without in- or out-edges are desired.
                            default = true
                            
    random_seed         =   (integer) random seed for pseudo-random number generator
                            default = system time (for stochastic results) 

__NOTES:__

* Network perturbations will always assume that activating edges are summed together. Activating edges that are multiplied will be recast into addition, potentially changing the size of the parameter graph.

* All networks are analyzed in essential mode, even if they are written in non-essential mode.

* Users can add query modules to the package `NetworkPerturbations.queries` for inclusion in parameter files. The required API is:

      newmodule.query(list_of_networks, results_directory_path, parameter_dict)

  Results are saved to a file within the `results_directory_path`. See the `queries` folder for already implemented queries.

    
* New filters can be implemented in `NetworkPerturbations.perturbations.filters`. It is recommended to use the `constrained_inedges` and `constrained_outedges` filters, since they may substantially reduce computation time.

# Network perturbations output

The list of DSGRN network specifications from the perturbation process is saved to a text file in the `results_directory_path`. To make into a Python list, open ipython and do
```
import ast
networks = ast.literal_eval(open("networks.txt").read())
```

# Query output

Query output is a `json` file that can be imported as a Python dictionary using 
```
import json
results = json.load(open("query_results.json"))
``` 
The keys are the DSGRN network specifications, and the values are usually `[#_matches, parameter_graph_size]`. However, the module `pattern_match` has a list of results of the form 
```
[[noise_lvl_1, #_matches, parameter_graph_size], [noise_lvl_2, #_matches, parameter_graph_size], ... ] 
``` 
See the modules in `queries` for details.

# Troubleshooting

The results from NetworkPerturbations can be unexpected due to the interplay between the input files and parameters. Here are some common things that can happen and their possible causes.

1. There are no networks produced after perturbation. 
    * The seed network has a node that has too many in-edges or too many out-edges, and the `probabilities` parameter has non-zero probabilities only for adding nodes and edges. In this case, no DSGRN computable networks can be constructed, because there will always be a non-computable subnetwork. At the time of this writing, 5 in-edges or 5 out-edges at a single node is likely too many (although not always). You must either (a) reduce the number of edges in your seed network, or (b) change your `probabilities` parameter so that removing nodes and/or edges is permitted.
      
     * The `maxparams` parameter may be too small. For example, if the seed network has 5000 parameters, but `maxparams` is 1000, and the `probabilities` parameter has non-zero probabilities only for adding nodes and edges, then no networks will be produced. To check the number of parameters for a seed network, repeat the previous steps and do
        ```
        import DSGRN
        network = DSGRN.Network("networkfile.txt")
        pg = DSGRN.ParameterGraph(network) 
        pg.size()
        ```
       where `"networkfile.txt"` is a single DSGRN network specification (i.e., is not a list of specifications).
     * The `node_file` path is specified, but points to an empty file, and the only non-zero `probabilities` parameter is `addNode`. 
    
     * The `edge_file` path is specified, but points to an empty file, and the only non-zero `probabilities` parameter is `addEdge`. 

     * The `edge_file` has only non-allowable edges, such as negative self-loops (which are never added to the network); or edges that can only result in a non-computable network and the `probabilities` for removing nodes and edges are zero.
         
     * The `edge_file` has only edges that connect nodes that are not in `node_file` or in the seed network.

2. There are many fewer networks produced than requested.
    * The `time_to_wait` parameter may be too small.
    * The specified `filters` may be too restrictive.
    * Network space may be too large. Restricting `range_operations` to a narrower interval may help.
    * Constraints in the `node_file` and `edge_file` lists of nodes and edges can limit the number of networks that is possible to construct. Be aware that files with few nodes and/or edges can reduce the number of permissible networks.
    * The `probabilities` parameter may emphasizing the wrong kind of operations. For example, if `addNode = 0.1` and `addEdge = 0.9`, but you only have 3 nodes, then there are very few networks that are likely to be created, and it will take a very long sampling time to find any networks with substantially more nodes. Note that there's an interplay with `range_operations` here. If `range_operations = [1,10]`, then you're likely to get at least a few networks with more nodes, but if `range_operations = [1,3]`, then it will be hard to find networks with more nodes.
    
3. There are no DSGRN query matches.
    * This probably means you are in the wrong part of network space. Repeat the process with a different seed network and/or different parameters.
    
4. You get an error when trying to query a specific network.
    * There are many causes of this. However, a common one is trying to query a network that is not DSGRN-computable.  To check if your network is computable, open ipython or a Jupyter notebook and do
        
        ``` 
        import DSGRN
        network = DSGRN.Network("networkfile.txt")
        pg = DSGRN.ParameterGraph(network) 
        ```
        if `"networkfile.txt"` has a single DSGRN network specification, or
        ```
        import ast, DSGRN
        networks = ast.literal_eval(open("networkfile.txt").read())
        network = DSGRN.Network(networks[0])
        pg = DSGRN.ParameterGraph(network) 
        ```
        if `"networkfile.txt"` has list syntax. If you get a `Could not find logic resource` error, then your network is not DSGRN computable, and you will have to make sure that every node has an out-edge, and that there are not too many in- or out-edges for any one node. At the time of this writing, 5 in-edges or 5 out-edges is likely too many (although not always). 