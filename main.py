import sys
import os
import cProfile, pstats, io
from functools import partial
from multiprocessing import Pool

from solver.dimacs_write import to_dimacs_str
from solver.lookaheadsolver import LookAHeadSolver
from solver.read import read_rules_dimacs as read_rules
from solver.read import read_text_sudoku as read_problem
from solver.solver import *
from solver.stats import print_stats, show_stats
from solver.visualizer import print_sudoku
from solver.restart_exception import RestartException

"""
    1. SAT Solver
        a. Datastructures
        b. 
    2. Read rules of sudoku (dimacs format)
    3. Read a specific sudoku
    4. solve that bitch
    5. Visualize solved sudoku
    6. Output to dimacs file
"""


def main(program_version: int, rules_dimacs_file_path: str):


    # sudoku_rules_clauses, last_id = read_rules(os.getcwd() + "/../data/sudoku-rules.txt", id=0)
    all_clauses, last_id = read_rules(rules_dimacs_file_path, id=0)

    # all_clauses = list(sudoku_clauses) + list(sudoku_clauses)
    knowledge_base = KnowledgeBase(all_clauses, clause_counter=last_id)

    solver = Solver(knowledge_base)

    solution, solved = solver.solve_instance()

    print_sudoku(solution)


def get_settings(program_version: int):

    if (program_version > 4):
        raise Exception("Program version should be between 1-4")

    if program_version == 3:
        return {}

    settings = {key: False for key in ["DependencyGraph", "Heuristiek2"]}
    if (program_version == 1):
        pass
    elif (program_version > 1):
        settings["DependencyGraph"] = True
        if (program_version > 2):
            settings["Heuristiek2"] = True

    return settings


def develop(program_version: int, rules_dimacs_file_path: str, problem_path: str):
    profile = False
    multiprocessing = True


    problems = list(range(0,100))

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
        else:
            sudokus_stats = list(map(solve_fn, problems))

        dm = DataManager(os.getcwd() + '/results/')
        dm.save_python_obj(sudokus_stats, f"experiment-v{program_version}")

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
    while (start):
        start = False

        try:
            print(f"\nStarting solving problem {problem_id}")
            print("Loading problem...")
            rules_clauses, last_id = read_rules(rules_dimacs_file_path, id=0)
            rules_puzzle, is_there_another_puzzle, last_id = read_problem(problem_path, problem_id, last_id)

            all_clauses = {**rules_clauses, **rules_puzzle}

            # all_clauses = list(sudoku_clauses) + list(sudoku_clauses)
            knowledge_base = KnowledgeBase(all_clauses, clause_counter=last_id)
            print("Problem loaded")

            if program_version == 3:
                solver = LookAHeadSolver(knowledge_base)
            else:
                solver = Solver(knowledge_base, split_stats=split_statistics, heuristics=settings)

            solution, solved, split_statistics = solver.solve_instance()


            print_sudoku(solution)
            # print_stats(split_statistics)
            dimacs = to_dimacs_str(solution)
            return (split_statistics, problem_id, program_version)

        except RestartException as e:

            start = e.restart

            if (start):
                print(f"Restarted {problem_id}")
                split_statistics = e.stats


if __name__ == "__main__":
    # Default vars:
    program_version = 1
    input_file = os.getcwd() + "/data/sudoku-rules.txt"

    if len(sys.argv) == 3:
        option = sys.argv[1]
        if len(option) != 3 or option[0:1] != '-S':
            raise RuntimeError("Invalid program option")
        program_version = int(option[2])

        input_file = sys.argv[2]

    # main(program_version, input_file)
    develop(3, input_file, os.getcwd() + "/data/sudokus/1000sudokus.txt")
