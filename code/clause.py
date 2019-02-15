from typing import Set, Any


class Clause(object):

    length: int
    id: int
    literals: Set[int]

    def __init__(self, id, literals):
        self.id = id
        self.literals = set(literals)
        self.length = len(self.literals)

    def __len__(self):
        return self.length


    def validate(self, assignment):
        pass

    def resolve(self, literal):
        pass

    def __str__(self):
        return str(self.literals)

    def __repr__(self):
        return self.__str__()

