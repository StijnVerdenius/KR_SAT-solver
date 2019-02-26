# KR_SAT-solver
### SAT-solver for course Knowledge Representation

#### Summary:

This repository contains an implementation of a SAT solver. 
Three versions are available as of now:

1. Standard Davis Putnam (DPLL)
2. Clause Driven Conflict Learning (CDCL)
3. Look-ahead SAT

#### Calling The Solver:

Arguments:

- -S#, where '\#' is the version you want to run
- [inputfile], which has to be in DIMACS format

Please call the solver using one of the following commands:

###### Linux/Mac-os:

    source SAT.sh -S# [inputfile]
    
or

    sh SAT.sh -S# [inputfile]
    
or

    . SAT.sh -S# [inputfile]
    
or 

    bash SAT.sh -S# [inputfile]
    
###### Windows (not tested, so no guarentee to work)

    SAT.bat -S# [inputfile]
    
#### Requirements:

Please make sure you have a working python version (3.5 or higher installed).
For packages, see the requirements.txt file.
If you have multiple python versions on your machine, make sure to activate an environment that can support all of the above, before calling the program

#### Overview of repository






