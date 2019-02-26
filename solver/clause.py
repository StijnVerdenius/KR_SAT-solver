from typing import Set, Dict, Tuple


class Clause(object):
    """
    Main class for clauses
    holds and id and a set of literals

    """

    id: int
    literals: Set[int]

    def __init__(self, id, literals):
        self.id = id
        self.literals = set(literals)

    def __len__(self):
        return len(self.literals)


    def remove_literal(self, literal):
        self.literals.remove(literal)

    def __str__(self):
        return str(self.literals)

    def __repr__(self):
        return self.__str__()

    def first(self):
        """
        Get the first literal in a set (without removing it)
        Fastest using for-loop
        Link: https://stackoverflow.com/questions/59825/how-to-retrieve-an-element-from-a-set-without-removing-it
        """

        for literal in self.literals:
            return literal
