from solver.knowledge_base import KnowledgeBase

try:
    import numpy as np
except ImportError:
    raise RuntimeError("Please install numpy")



def print_sudoku(base : KnowledgeBase, shape = (9, 9)):
    sudoku = np.zeros(shape)

    literals = list(filter(lambda x: x > 0,base.current_set_literals.keys()))
    for literal in literals:

        # if (clause.length > 1):
        #     raise Exception("Not-unit-clause in base")
        #
        # literal = clause.literals.pop()
        #
        # if literal < 1:
        #     raise Exception("Non-positive literal")


        x = int(str(literal)[0]) - 1
        y = int(str(literal)[1]) - 1

        if sudoku[x, y] != 0:
            # raise Exception(">>??")
            pass
        value = int(str(literal)[2])

        sudoku[x, y] = value

    print(sudoku)