import os
from typing import Dict, Tuple
from solver.clause import Clause
try:
    import numpy as np
except ImportError:
    raise RuntimeError("Please install numpy")
import math

def read_rules_string(rules_str: str, id: int) -> Tuple[Dict[int, Clause], int]:
    # TODO: error on file nt found
    clauses = {}
    for line in rules_str.split("\t"):
        tokens = line.split(' ')
        if tokens[-1] != '0\n':
            continue

        literals = [int(token) for token in tokens[0:-1]]

        clauses[id] = Clause(id, literals)
        id += 1

    return clauses, id

def read_rules_dimacs(rules_path: str, id: int) -> Tuple[Dict[int, Clause], int]:
    # TODO: error on file nt found
    with open(rules_path) as f:

        stringbuilder = "{}"

        for line in f:
            stringbuilder = stringbuilder.format(line+"\t{}")

    return read_rules_string(stringbuilder.replace("\n{}", ""), id)

def read_text_sudoku(puzzle_path: str, puzzle_number: int, id: int) -> Tuple[Dict[int, Clause], bool, int]:

    with open(puzzle_path) as f:
        for i, line in enumerate(f):

            if (i == puzzle_number):

                print(line)

                line = line.replace("\n", "")

                template = np.zeros((len(line), 1))

                for j, letter in enumerate(line):

                    if (not letter == "."):

                        try:

                            template[j,0] = int(letter)

                        except ValueError:

                            continue

                template = template.reshape((int(math.sqrt(len(line))), int(math.sqrt(len(line)))))

                # print(template)

                output = "{}"

                for y in range(len(template)):

                    for x in range(len(template)):

                        if (not template[y,x] == 0):
                            output = output.format(str(x+1)+str(y+1)+str(int(template[y,x]))+" 0\n\t{}")

                returnvalues = read_rules_string(output.replace("\n{}", ""), id)

                return returnvalues[0], True, returnvalues[1]

    return None, False, id



if __name__ == "__main__":
    rules_path = os.getcwd() + "/../data/sudoku-rules.txt"
    sudoku_path = os.getcwd() + "/../data/sudoku-example.txt"

    clauses = read_rules_dimacs(rules_path)
    print("Rules:", list(clauses))

    clauses = list(read_rules_dimacs(sudoku_path))
    expected = [{168}, {175}, {225}, {231}, {318}, {419}, {444}, {465}, {493}, {689}, {692}, {727}, {732}, {828}, {886}, {956}, {961}, {973}]

    assert str(clauses) == str(expected)

    print(read_text_sudoku(os.getcwd() + "/../data/sudokus/1000sudokus.txt", 1)[1])



