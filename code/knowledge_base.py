from collections import defaultdict
from typing import List, Dict, Set
from code.clause import Clause

class KnowledgeBase:

    bookkeeping: Dict[int, Set[int]]
    clauses: Dict[int, Clause]
    current_truth_values: Dict[int, bool]

    def __init__(self, clauses = None, current_truth_values = None, bookeeping = None, counter = 0, literal_set = None):

        # clauses
        if clauses is None:
            self.clauses = {}
        else:
            self.clauses = clauses

        # current assignment for literals
        if current_truth_values is None:
            self.current_truth_values = {}
        else:
            self.current_truth_values = current_truth_values

        # bookkeeping references
        if bookeeping is None:
            self.bookkeeping = defaultdict(set)
            for clause in clauses.values():
                for literal in clause.literals:
                    self.bookkeeping[literal].add(clause.id)
        else:
            self.bookkeeping = bookeeping

        # counts amount of clauses
        self.clause_counter = counter

        # keeping track of the amount of literals
        if literal_set is None:
            self.literal_set = set()
        else:
            self.literal_set = literal_set


    def validate(self):
        pass

    def insert_rules(self, rules):
        """ inserts rules to knowledge base """

        for rule in rules:
            self.clauses.append(Clause(self.clause_counter, rule))
            for literal in rule:
                self.literal_set.add(literal)
                self.bookkeeping[literal].add(self.clause_counter)
            self.clause_counter += 1

    def simplify(self):

        self.simplify_unit_clauses()
        self.simplify_pure_literal()

    def simplify_unit_clauses(self):
        for id in self.clauses:
            if (self.clauses[id].length == 1):
                literal = self.clauses[id].literals.pop()
                self.set_literal(literal, literal>0)

    def simplify_pure_literal(self):

        for literal in self.literal_set:

            attempt = set()

            for id in self.bookkeeping[literal]:
                if (len(attempt) > 1):
                    break

                if (literal in self.clauses[id].literals):
                    attempt.add(True)
                elif ((- literal) in self.clauses[id].literals):
                    attempt.add(False)

            if (len(attempt) == 1):
                value = attempt.pop()
                self.set_literal(literal, value)

    def tautology_simplify(self):
        # Currently O(N^2) check
        clauses_to_remove = []
        for clause in self.clauses.values():
            if any(-literal in clause.literals for literal in clause.literals):
                clauses_to_remove.append(clause)

        self.remove_clauses(clauses_to_remove)

    def set_literal(self, literal: int, truth_value: bool) -> bool:
        """
        Set a literal and its boolean value
        :param literal:
        :param truth_value:
        """
        # First check if this is a allowed op.
        for clause_id in self.bookkeeping[literal]:
            clause = self.clauses[clause_id]
            if len(clause.literals) == 1 and -literal in clause.literals:
                return False

        # Set literal
        self.current_truth_values[literal] = truth_value
        clauses_to_remove = []
        for clause_id in self.bookkeeping[literal]:
            clause = self.clauses[clause_id]

            # If we set P to true and ~P is set, we can remove the literal
            if -literal in clause.literals:
                clauses_to_remove.append(clause)
                continue

            clause.literals.remove(literal)

            # Remove empty and satisfied clauses
            if len(clause.literals) == 0:
                clauses_to_remove.append(clause)

        self.remove_clauses(clauses_to_remove)
        self.bookkeeping[literal].pop()

        return True


    def remove_clauses(self, clauses_to_remove: List[Clause]):
        """
        Remove list of clauses from KB
        :param clauses_to_remove:
        """
        for clause in clauses_to_remove:
            self.clauses.pop(clause.id, None)
            for literal in clause.literals:
                self.bookkeeping[literal].remove(clause.id)
