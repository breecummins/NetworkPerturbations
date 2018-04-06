This module accepts a network in DSGRN network specification format, generates a collection of networks in the neighborhood of the first, perhaps constrained by certain nodes and edges, and performs a DSGRN query on every parameter of every network.

Dependencies: Python 3.6, numpy, DSGRN (https://github.com/shaunharker/DSGRN) and dependencies

Calling script is libnetperturb/perturbations/main.py:

python main.py <params.json>

See example parameter files in the examples folder. The keywords in the json parameter dictionary are given as follows.

REQUIRED:

querymodule         =   module name from queries that has the query to be performed

computationsdir     =   path to location where results are to be stored;
                        empty string "" indicates current directory

networkfile         =   path to a file containing either a single network specification (see example_networkspec.txt),
                        or a comma-separated list of them (see example_networklist.txt)

makeperturbations   =   true or false (must be lower case, no quotes);
                        false = perform the query only for the network specifications provided in the list;
                        true = for every network spec in the list, make perturbations using the parameters below

IF MAKEPERTURBATIONS == TRUE, THE FOLLOWING ARE REQUIRED EXCEPT WHERE NOTED:

    nodefile            =   OPTIONAL: path to file containing the names of nodes to add, one line per name;
                            or empty string "" or missing keyword if no such file exists

    edgefile            =   OPTIONAL: path to file containing named edges to add, one per line,
                            in the form TARGET_NODE = TYPE_REG(SOURCE_NODE),
                            where TYPE_REG  is a (activation) or r (repression);
                            or empty string "" or missing keyword if no such file exists

    add_anon_nodes      =   true or false (must be lower case, no quotes) to add unnamed nodes to the perturbed networks

    swap_edge_reg       =   true or false (must be lower case, no quotes) to allow the sign of regulation to be swapped
                            on edges in the original network

    numperturbations    =   Maximum number of perturbed networks to find (integer);
                            process may time out before this number is reached

    maxaddspergraph     =   Maximum number of node/edge perturbations (integer) to allow in each perturbed graph

    maxparams           =   Maximum number of parameters (integer) allowed for DSGRN computations

    time_to_wait        =   Maximum time in seconds (integer) allowed to calculate perturbed networks;
                            intended as a fail-safe when there are not enough computable networks in the neighborhood;
                            does not affect queryfile computation time

OTHER KEYS ADDED AS NEEDED TO THE DICTIONARY FOR THE CHOSEN QUERY MODULE, WHICH MAY REQUIRE ADDITIONAL ARGUMENTS.

NOTES:

(1) Users can add query modules to the package libnetperturb.queries for inclusion in parameter files.
    The required API is:

    newmodule.query(list_of_networks, results_directory_path, parameter_dict)

    See CountFPMatch.py and CountStableFC.py for examples.

(2) Network perturbations will always assume that activating edges are summed together. Activating edges that are multiplied will be recast into addition, potentially changing the size of the parameter graph.