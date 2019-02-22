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
        self.literals = frozenset(literals)

    def __len__(self):
        return len(self.literals)

    def validate(self, assigned_literals: Dict[int, bool]) -> Tuple[bool, bool]:
        """
        Evaluates the clause against a assignment of literals
        :param assigned_literals:
        :return: boolean
        """

        for literal in self.literals:
            literal = abs(literal)
            if literal not in assigned_literals:
                continue

            assignment = assigned_literals[literal]
            if literal < 0 and assignment is False:
                return True, False

            if literal > 0 and assignment is True:
                return True, False

        return False, False

    def remove_literal(self, literal):
        self.literals = self.literals - frozenset([literal])

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
