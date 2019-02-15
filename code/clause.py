

class Clause(object):

    def __init__(self, id, literals):
        self.id = id
        self.literals = literals
        self.length = len(self.literals)

    def __len__(self):
        return self.length


    def validate(self, assignment):
        pass

    def resolve(self, literal):
        pass

