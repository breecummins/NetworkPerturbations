This module accepts a network in DSGRN network specification format, generates a collection of networks in the neighborhood of the first, perhaps constrained by certain nodes and edges, and performs a DSGRN query on every parameter of every network.

Dependencies: Python 3.6+, numpy, networkx, multiprocessing, pandas, and DSGRN (https://github.com/shaunharker/DSGRN) and dependencies

To install, do
    
    cd NetworkPerturbations
    . install.sh

To run tests to confirm the code is working as expected, do

    cd tests
    pytest

Calling script is `scripts/call_job.py`:

    python call_job.py <params.json>
    

See the parameter files in the `tests` folder for examples of the input argument to `call_jobs.py`. The keywords in the json parameter dictionary are given as follows.

REQUIRED:

    querymodule         =   module name from queries that has the query to be performed
    
    querymodule_args    =   dictionary containing query module specific arguments -- see 
                            individual query documentation. Can be empty for some queries.

    computationsdir     =   path to location where results are to be stored; 
                            empty string "" indicates current directory

    networkfile         =   path to a file containing either a single network specification
                            or a list of them (comma-separated and surrounded by square
                            brackets, saved as plain text)

    makeperturbations   =   true or false (must be lowercase, no quotes);
                            false = perform the query only for the network specifications 
                                    provided in the list;
                            true = for every network spec in the list, 
                                   make perturbations using the parameters below


If makeperturbations == true, the following are optional parameters with the defaults listed:

    probabilities      =   dictionary with operations keying the probability that the operation will occur
                           default = 
                           {"addNode" : 0.50, "removeNode" : 0.0, "addEdge" : 0.50, "removeEdge" : 0.0}
                           NOTE: "removeNode" is not currently supported and must be set to zero. 
                           Make a feature request if you need it.
                          

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

    filters             =   dictionary of filter function name strings from filters.py keying input 
                            dictionaries with the needed keyword arguments for each function
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

NOTES:

* Network perturbations will always assume that activating edges are summed together. Activating edges that are multiplied will be recast into addition, potentially changing the size of the parameter graph.

* All networks are analyzed in essential mode, even if they are written in non-essential mode.

* Users can add query modules to the package `NetworkPerturbations.queries` for inclusion in parameter files. The required API is:

    newmodule.query(list_of_networks, results_directory_path, parameter_dict)

  Results are saved to a file within the `results_directory_path`. See the `queries` folder for already implemented queries.

    
* New filters can be implemented in `NetworkPerturbations.perturbations.filters`. It is recommended to use the `constrained_inedges` and `constrained_outedges` filters, since they may substantially reduce computation time.

