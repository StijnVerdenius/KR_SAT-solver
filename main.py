import sys
import os
import cProfile, pstats, io
from functools import partial
from multiprocessing import Pool

from implementation.solver.solver_lookahead import LookAHeadSolver

from implementation.model.exception_implementations import RunningTimeException
from implementation.solver.solver_cdcl_dpll import *
from implementation.util.visualizer import print_sudoku
from implementation.model.exception_implementations import RestartException
from implementation.util.data_management import DataManager


#### Constants
MIN_ARGUMENTS = 3
MAX_ARGUMENTS = 3
MAX_VERSION = 3
MIN_VERSION = 1
MIN_PYTHON = 3
MIN_PYTHON_SUB = 5
DEPGRAPH = "DependencyGraph"
LOOKAHEAD = "Lookahead"
RETRYLIMIT = 5

data_manager = DataManager(os.getcwd() + '/results/')


def main(program_version: int, rules_dimacs_file_path: str):
    """
    Main function for solving dimacs

    :param program_version:
    :param rules_dimacs_file_path:
    :return:
    """
    for try_count in range(RETRYLIMIT):
        try:

            # get settings
            settings = get_settings(program_version)

            # load clauses
            all_clauses, last_id = data_manager.read_rules_dimacs(rules_dimacs_file_path, id=0)

            # init implementation
            solver = get_solver(all_clauses, last_id, settings)

            # retrieve solution
            solution, solved, stats = solver.solve_instance()

            # get dimacs
            dimacs =data_manager.to_dimacs_str(solution)

            # save to file
            file = open(rules_dimacs_file_path+".out", "w")
            file.write(dimacs+"\n")
            file.close()

            # notify user
            print("\n\n\nFINISHED: Solved and written to file successfully")
            sys.exit(0)

        except RestartException:
            print(f"Restarted")

    raise Exception(f"Tried {RETRYLIMIT} times, could not get a valid answer")


def get_solver(clauses : Dict[int, Clause], last_id : int, settings: Dict[str, bool]):
    """ Retrieves implementation fit to version """

    # build knowledge base
    kb = KnowledgeBase(clauses, clause_counter=last_id, dependency_graph=settings[DEPGRAPH])

    # init implementation
    if (settings[LOOKAHEAD]):
        solver = LookAHeadSolver(kb)
    else:
        solver = CDCL_DPLL_Solver(kb,  heuristics=settings)

    return solver

def get_settings(program_version: int):
    """
    Get settings for run

    :param program_version:
    :return:
    """

    if (program_version > MAX_VERSION or program_version < MIN_VERSION):
        raise Exception("Program version should be between 1-3")

    if program_version == 3:
        return {DEPGRAPH : False, LOOKAHEAD : True}
    elif (program_version == 1):
        return {DEPGRAPH : False, LOOKAHEAD : False}
    elif (program_version == 2):
        return {DEPGRAPH : True,  LOOKAHEAD: False}

def enforce_python_version():
    """
    Enforces correct python version for run

    :return:
    """

    inf = sys.version_info
    if (inf[0] < MIN_PYTHON or inf[1] < MIN_PYTHON_SUB):
        raise Exception("\n\n####################\nMake sure correct version of python is installed (3.5 or higher)\n####################\n\n")


def parse_arguments(arguments):
    """
    Parses argument

    :param arguments:
    :return:
    """
    number_of_arguments = len(arguments)
    if (number_of_arguments < MIN_VERSION or number_of_arguments > MAX_ARGUMENTS):
        raise Exception(f"You gave {number_of_arguments} arguments while it should be between {MIN_ARGUMENTS} - {MAX_ARGUMENTS}")

    option = arguments[1]
    if len(option) != 3 or option[0:2] != '-S':
        raise RuntimeError("Invalid program option")

    program_version = int(option[2])

    input_file = os.getcwd() + arguments[2]

    return program_version, input_file

if __name__ == "__main__":

    # check env
    enforce_python_version()

    # get arguments
    program_version, input_file = parse_arguments(sys.argv)

    # run
    main(program_version, input_file)

    # exit successfully
    sys.exit(0)
