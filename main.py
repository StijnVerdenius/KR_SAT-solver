import sys
import os

from solver.knowledge_base import KnowledgeBase
from solver.read import read_rules
from solver.solver import *
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



def main(program_version: int, dimacs_file_path: str):
    import cProfile, pstats, io
    pr = cProfile.Profile()
    pr.enable()

    # sudoku_rules_clauses, last_id = read_rules(os.getcwd() + "/../data/sudoku-rules.txt", id=0)
    all_clauses, last_id = read_rules(dimacs_file_path, id=0)

    # all_clauses = list(sudoku_clauses) + list(sudoku_clauses)
    knowledge_base = KnowledgeBase(all_clauses, counter=last_id)

    solver = Solver(knowledge_base)

    solution, solved = solver.solve_instance()

    print_sudoku(solution)

    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())





if __name__ == "__main__":
    # Default vars:
    program_version = 1
    input_file = os.getcwd() + "/data/sudoku-example.txt"

    if len(sys.argv) == 3:
        option = sys.argv[1]
        if len(option) != 3 or option[0:1] != '-S':
            raise RuntimeError("Invalid program option")
        program_version = int(option[2])

        file = sys.argv[2]

    main(program_version, input_file)


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