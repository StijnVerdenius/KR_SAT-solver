import sys
import os
import cProfile, pstats, io
from functools import partial
from multiprocessing import Pool

from solver.dimacs_write import to_dimacs_str
from solver.lookaheadsolver import LookAHeadSolver
from solver.read import read_rules_dimacs as read_rules
from solver.read import read_text_sudoku as read_problem
from solver.running_time_exception import RunningTimeException
from solver.solver import *
from solver.stats import print_stats, show_stats
from solver.visualizer import print_sudoku
from solver.restart_exception import RestartException


#### Constants
MIN_ARGUMENTS = 3
MAX_ARGUMENTS = 3
MAX_VERSION = 3
MIN_VERSION = 1
MIN_PYTHON = 3
MIN_PYTHON_SUB = 5


def main(program_version: int, rules_dimacs_file_path: str):
    """ main function for solving dimacs """

    settings = get_settings(program_version)

    # sudoku_rules_clauses, last_id = read_rules(os.getcwd() + "/../data/sudoku-rules.txt", id=0)
    all_clauses, last_id = read_rules(rules_dimacs_file_path, id=0)

    knowledge_base = KnowledgeBase(all_clauses, clause_counter=last_id)

    solver = Solver(knowledge_base)

    solution, solved, stats = solver.solve_instance()

    dimacs = to_dimacs_str(solution)

    file = open(rules_dimacs_file_path+".out", "w")

    file.write(dimacs+"\n")

    file.close()

    print("Solved and written to file sucessfully")


def get_settings(program_version: int):
    """
    Get settings for run

    :param program_version:
    :return:
    """

    if (program_version > MAX_VERSION or program_version < MIN_VERSION):
        raise Exception("Program version should be between 1-3")

    if program_version == 3:
        return {"DependencyGraph" : False, "Lookahead" : True}
    elif (program_version == 1):
        return {"DependencyGraph" : False, "Lookahead" : False}
    elif (program_version == 2):
        return {"DependencyGraph" : True, "Lookahead" : False}



def develop(program_version: int, rules_dimacs_file_path: str, problem_path: str):
    profile = False
    multiprocessing = False


    problems = range(0,999)

    if profile:
        pr = cProfile.Profile()
        pr.enable()

    for program_version in [2, 3]:
        settings = get_settings(program_version)
        print("SETTINGS:", settings)

        solve_fn = partial(solve_sudoku, problem_path=problem_path, program_version=program_version, rules_dimacs_file_path=rules_dimacs_file_path, settings=settings)
        if multiprocessing:
            p = Pool(12)
            sudokus_stats = list(p.map(solve_fn, problems))
            sudokus_stats = list(filter(lambda x: x[0] is not None, sudokus_stats))
        else:
            sudokus_stats = map(solve_fn, problems)
            sudokus_stats = list(filter(lambda x: x[0] is not None, sudokus_stats))

        # dm = DataManager(os.getcwd() + '/results/')
        # dm.save_python_obj(sudokus_stats, f"experiment-v{program_version}")

    if profile:
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())


def solve_sudoku(problem_id, problem_path, program_version, rules_dimacs_file_path, settings):
    print(f"problem: {problem_id}")
    start = True
    split_statistics = []
    runtime = None
    while (start):
        start = False


        try:
            print(f"\nStarting solving problem {problem_id}, program_version: {program_version}")
            print("Loading problem...")
            rules_clauses, last_id = read_rules(rules_dimacs_file_path, id=0)
            # rules_puzzle, is_there_another_puzzle, last_id = read_problem(problem_path, problem_id, last_id)

            # all_clauses = {**rules_clauses, **rules_puzzle}

            # all_clauses = list(sudoku_clauses) + list(sudoku_clauses)
            knowledge_base = KnowledgeBase(rules_clauses, clause_counter=last_id)
            print("Problem loaded")

            if settings["Lookahead"]:
                solver = LookAHeadSolver(knowledge_base)
            else:
                solver = Solver(knowledge_base, split_stats=split_statistics, heuristics=settings, problem_id=problem_id, start=runtime)

            try:
                solution, solved, split_statistics = solver.solve_instance()

                # print_sudoku(solution)
            except RunningTimeException as e:
                print(f"!!! SKIPPED SUDOKU {problem_id} !!!")
                print(e)
                return (None, None, None)

            # print_stats(split_statistics)
            #dimacs = to_dimacs_str(solution)
            return (split_statistics, problem_id, program_version)

        except RestartException as e:

            start = e.restart

            if (start):
                print(f"Restarted {problem_id}")
                split_statistics = e.stats
                runtime = e.runtime

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

    input_file = arguments[2]

    return program_version, input_file

if __name__ == "__main__":

    enforce_python_version()

    program_version, input_file = parse_arguments(sys.argv)

    # Default vars:
    program_version = 1 # TODO: REMOVE DEFAULT
    # input_file = os.getcwd() + "/data/sudokus/uf20-01.cnf"
    input_file = os.getcwd() + "/data/sudoku-rules.txt"

    # main(program_version, input_file)
    develop(program_version, input_file, os.getcwd() + "/data/sudokus/1000sudokus.txt")

