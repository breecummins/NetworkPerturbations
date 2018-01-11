Keywords in the parameter dictionary. See example_paramdict.json for format.

REQUIRED:

queryfile           =   path to python script that performs desired DSGRN queries;
                        this includes pattern matching and making posets of extrema if desired (see make_patterns.py);
                        the main calling function inside this script should be named query() and take two arguments,
                        a list of networks and a path to a results directory (see example_query.py)

computationsdir     =   path to location where results are to be stored;
                        "./" indicates current directory

networkfile         =   path to a file containing either a single network specification (see example_networkspec.txt),
                        or a comma-separated list of them (see example_networklist.txt)

makeperturbations   =   true or false (must be lower case, no quotes);
                        false = perform the query only for the network specifications provided in the list;
                        true = for every network spec in the list, make perturbations using the parameters below

IF MAKEPERTURBATIONS == TRUE, THE FOLLOWING ARE REQUIRED EXCEPT WHERE NOTED:

    nodefile            =   OPTIONAL: path to file containing the names of nodes to add, one line per name;
                            or empty string or missing keyword if no such file exists

    edgefile            =   OPTIONAL: path to file containing named edges to add, one per line,
                            in the form (node1, node2, "a" or "r"),
                            where "a" means activation and "r" means repression;
                            or empty string or missing keyword if no such file exists

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

