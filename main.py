import sys
import os
import cProfile, pstats, io
from multiprocessing import Pool

from solver.dimacs_write import to_dimacs_str
from solver.knowledge_base import KnowledgeBase
from solver.read import read_rules_dimacs as read_rules
from solver.read import read_text_sudoku as read_problem
from solver.solver import *
from solver.stats import print_stats, show_stats
from solver.visualizer import print_sudoku

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


def develop(program_version: int, rules_dimacs_file_path: str, problem_path: str):
    profile = True

    if profile:
        pr = cProfile.Profile()
        pr.enable()

    problems = range(0, 24)
    # problems = range(0, 10)

    # p = Pool(12)
    # results = p.map(solve_sudoku, problems)
    # sudokus_stats = list(filter(lambda x: x is not None, results))

    sudokus_stats = []
    for problem_id in problems:

        print(f"Solving problem {problem_id}")
        rules_clauses, last_id = read_rules(rules_dimacs_file_path, id=0)
        rules_puzzle, is_there_another_puzzle, last_id = read_problem(problem_path, problem_id, last_id)

        all_clauses = {**rules_clauses, **rules_puzzle}

        # all_clauses = list(sudoku_clauses) + list(sudoku_clauses)
        knowledge_base = KnowledgeBase(all_clauses, clause_counter=last_id)
        solver = Solver(knowledge_base)

        try:
            solution, solved, split_statistics = solver.solve_instance()
        except RunningTimeException as e:
            print(e)
            continue

        sudokus_stats.append((split_statistics, problem_id))

        print_sudoku(solution)
        # print_stats(split_statistics)
        dimacs = to_dimacs_str(solution)

    show_stats(sudokus_stats)

    if profile:
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

def solve_sudoku(problem_id):
    print(f"Solving problem {problem_id}")
    problem_path = os.getcwd() + "/data/sudokus/1000sudokus.txt"
    rules_dimacs_file_path = os.getcwd() + "/data/sudoku-rules.txt"
    rules_clauses, last_id = read_rules(rules_dimacs_file_path, id=0)
    rules_puzzle, is_there_another_puzzle, last_id = read_problem(problem_path, problem_id, last_id)

    all_clauses = {**rules_clauses, **rules_puzzle}

    # all_clauses = list(sudoku_clauses) + list(sudoku_clauses)
    knowledge_base = KnowledgeBase(all_clauses, clause_counter=last_id)
    solver = Solver(knowledge_base)

    try:
        solution, solved, split_statistics = solver.solve_instance()
    except RunningTimeException as e:
        print(e)
        return None

    # sudokus_stats.append((split_statistics, problem_id))

    print_sudoku(solution)
    # print_stats(split_statistics)
    dimacs = to_dimacs_str(solution)

    return (split_statistics, problem_id)


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
    develop(0, input_file, os.getcwd() + "/data/sudokus/1000sudokus.txt")


# import cProfile, pstats, io
# pr = cProfile.Profile()
# pr.enable()
#
# for x in range(10000):
#     test_solver_case3()
#
# pr.disable()
# s = io.StringIO()
# sortby = 'cumulative'
# ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
# ps.print_stats()
# print(s.getvalue())