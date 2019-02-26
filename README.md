# KR_SAT-solver
### SAT-solver for course Knowledge Representation

----

#### Summary:

This repository contains an implementation of a SAT solver. 
Three versions are available as of now:

1. Standard Davis Putnam (DPLL)
2. Clause Driven Conflict Learning (CDCL)
3. Look-ahead SAT

#### Calling The Solver:

Arguments:

- -S#, where '\#' is the version you want to run
- [inputfile], which has to be in DIMACS cnf format

Please call the solver using one of the following commands:

###### Linux/Mac-os:

    source SAT.sh -S# [inputfile]
    
*or* 

    sh SAT.sh -S# [inputfile]
    
*or* 

    . SAT.sh -S# [inputfile]
    
*or* 

    bash SAT.sh -S# [inputfile]
    
###### Windows (not tested, so no guarentee to work)

    SAT.bat -S# [inputfile]
    
*or install something to call sh files and call:*

    sh SAT.sh -S# [inputfile]
    
#### Requirements:

Please make sure you have a working python version (3.5 or higher installed).
For packages, see the requirements.txt file.
If you have multiple python versions on your machine, make sure to activate an environment that can support all of the above, before calling the program

#### Overview of repository:

The repository has a few python files that do all the work:

- **solver**: main solver parent class
- **solver_cdcl_dpll**: extends solver and implements version 1 & 2
- **solver_lookahead**: extends solver and implements version 3
- **knowledge_base**: hold information about one state in the search tree
- **data_management**: does file saving, loading and deepcopying
- **visualizer**: can print sudokus and visualize statistics
- **main**: parses commands and takes the right action accordingly

On top of that there are a few classes that simply hold data:

- **dependency_graph**: data sctructure for CDCL (version 2)
- **clause**: a single clause in cnf
- **exception implementations** holds some exceptions that are used for solve-flow
- **split**: container for some statistics

#### Implementation specification:

The algorithms have been implemented using a stack, in which the search tree is expanded and also where backtracking is performed.
Every loop the algorithm chooses a next state, tries to simplify it and then does a split. If an error situation in any of these steps is detected, a backtracking will be triggered.
The algorithm uses a form of bookeeping to know which literals are present in which clauses and a combination of ordered list and lookup dictionary to build the stack and do backtracking.
In each individual node of the search tree there is a state of the type 'Knowledge Base' that holds the information about the still existing clauses, the already found literal allocation and the bookeeping. By efficient copying this state we can model each state of the search tree this way and backtrack quickly to previous decision nodes.

In version two a dependency graph has been added to the Knowledge Base as well, holding information about which assignment led to the next. This way when an incosnsistency arises a problem clause can be added to the knowledge base and there can be backtracked accordingly to the right node.

Also in the third version more addition is done to the implementation. Namely, TODO: Max



