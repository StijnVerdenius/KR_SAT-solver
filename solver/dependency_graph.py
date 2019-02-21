
from collections import defaultdict
from solver.clause import Clause



class DependencyGraph:

    def __init__(self, initial=None, graph = None, existing_literals = None, bookkeeping=None, clauses=None):

        if (initial is None):
            self.initial_coocurrence = defaultdict(set)

            for key in bookkeeping:
                for id in bookkeeping[key]:
                    for literal in clauses[id].literals:
                        self.initial_coocurrence[key].add(literal)
        else:
            self.initial_coocurrence = initial

        if (graph == None):
            self.graph = defaultdict(set)
        else:
            self.graph = graph

        if (existing_literals == None):
            self.existing_literals = []
        else:
            self.existing_literals = existing_literals


    def add_literal(self, literal):

        cooccuring = self.initial_coocurrence[literal]
        for cooc_literal in cooccuring:
            if (abs(cooc_literal) in self.existing_literals):
                self.graph[literal].add(-cooc_literal)

        self.existing_literals.append(literal)

    def find_conflict_clause(self, literal, id):

        return Clause(id, self.graph[literal])

    def find_backtrack_node(self, literal):

        for literal in self.graph[literal]:
            pass
