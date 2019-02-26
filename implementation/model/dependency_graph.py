
from collections import defaultdict
from implementation.model.clause import Clause
from typing import Dict, Set




class DependencyGraph:

    """
    Holds the dependency graph functionality
    """

    initial_coocurrence: Dict[int, Set[int]]
    graph: Dict[int, Set[int]]

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
        """
        Adds literal into dependency graph

        :param literal:
        :param split:
        :return:
        """

        if (not split):

            self.graph[literal].update([lit for lit in self.initial_coocurrence[literal] if abs(lit) in self.existing_literals])

        self.existing_literals.append(literal)

    def find_conflict_clause(self, literal, id):
        """
        Finds the conflict clause given the literal that generated the conflict

        :param literal:
        :param id:
        :return:
        """

        return Clause(id, self.graph[literal])
