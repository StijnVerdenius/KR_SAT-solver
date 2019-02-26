from implementation.solver.knowledge_base import KnowledgeBase

try:
    import numpy as np
except ImportError:
    raise RuntimeError("Please install numpy package")



def print_sudoku(base : KnowledgeBase, shape = (9, 9)):
    sudoku = np.zeros(shape)

    literals = list(filter(lambda x: x > 0,base.current_set_literals.keys()))
    for literal in literals:

        if (not base.current_set_literals[literal]):
            # not true literal
            continue

        x = int(str(literal)[0]) - 1
        y = int(str(literal)[1]) - 1

        if sudoku[x, y] != 0:
            raise Exception("Contrasting entries")

        value = int(str(literal)[2])

        sudoku[x, y] = value

    print(sudoku.T)