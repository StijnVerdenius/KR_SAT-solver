from code.knowledge_base import *
try :
    import numpy as np

    class Visualizer:

        def __init__(self):
            pass

        def print_sudoku(self, base : KnowledgeBase, shape = (9, 9)):

            sudoku = np.zeros(shape)

            for clause in base.clauses:

                if (clause.length > 1):
                    raise Exception("Not-unit-clause in base")

                literal = clause.literals.pop()

                if (literal < 1):
                    raise Exception("Non-positive literal")

                x = int(str(literal)[0])
                y = int(str(literal)[1])
                value = int(str(literal)[2])

                sudoku[x,y] = value

            print(sudoku)

except:

    print("Please install numpy")