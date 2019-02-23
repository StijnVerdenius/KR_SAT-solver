
from collections import defaultdict
from solver.clause import Clause



class DependencyGraph:

    def __init__(self, initial=None, graph = None, existing_literals = None, bookkeeping=None, clauses=None):

        if (initial is None):
            self.initial_coocurrence = defaultdict(set)

            for key in bookkeeping:
                for id in bookkeeping[key]:
                    for literal in [lit for lit in clauses[id].literals if not abs(lit) == key]:
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

    def add_literal(self, literal, split=False):

        if (not split):
            # cooccuring = self.initial_coocurrence[literal]
            # for cooc_literal in cooccuring:
            #     if (abs(cooc_literal) in self.existing_literals):
            #         self.graph[literal].add(cooc_literal)  # todo: dont delete this just in case <<<<

            self.graph[literal].update([lit for lit in self.initial_coocurrence[literal] if abs(lit) in self.existing_literals])

        self.existing_literals.append(literal)

    def find_conflict_clause(self, literal, id):

        return Clause(id, self.graph[literal])
