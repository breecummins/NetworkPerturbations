Main script is main.py. Call from within inputfiles as

python ../perturbations/main.py <params.json>


Keywords in the json parameter dictionary. See examples in inputfiles/ for format.

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

(2) Network perturbations will always assume that activating edges are summed together. Activating edges that are
multiplied will be recast into addition, potentially changing the size of the parameter graph.