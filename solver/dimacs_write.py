from solver.knowledge_base import KnowledgeBase


def to_dimacs_str(knowledge_base: KnowledgeBase):
    file = []
    literals = list(filter(lambda x: x > 0, knowledge_base.current_set_literals.keys()))
    file.append("p cnf 81 90")
    for literal in literals:

        if (not knowledge_base.current_set_literals[literal]):
            # not true literal
            continue

        file.append(f"{literal} 0\n")
        # x = int(str(literal)[0]) - 1
        # y = int(str(literal)[1]) - 1
        #
        # if sudoku[x, y] != 0:
        #     raise Exception("Contrasting entries")
        #
        # value = int(str(literal)[2])
        #
        # sudoku[x, y] = value

    return "".join(file)



