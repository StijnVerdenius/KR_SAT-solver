from solver.knowledge_base import KnowledgeBase


def to_dimacs_str(knowledge_base: KnowledgeBase):
    """
    Transfers knowledge base back to dimacs (string)

    :param knowledge_base:
    :return:
    """

    file = []
    literals = list(filter(lambda x: x > 0, knowledge_base.current_set_literals.keys()))
    file.append("p cnf 81 90")
    for literal in literals:

        if (not knowledge_base.current_set_literals[literal]):
            continue

        file.append(f"{literal} 0\n")

    return "".join(file)



