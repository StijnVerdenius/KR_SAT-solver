from collections import defaultdict, namedtuple
from typing import List, Dict, Set, Tuple
from solver.clause import Clause


class KnowledgeBase:
    """
    knowledge base class

    holds main functionality for a knowledge base, including operations on its data

    contains:
    - clauses
    - bookkeeping
    - current assignments
    - todo: dependency graph?

    """

    bookkeeping: Dict[int, Set[int]]
    clauses: Dict[int, Clause]
    current_set_literals: Dict[int, bool]

    def __init__(self, clauses = None, current_set_literals = None, bookkeeping = None, clause_counter = 0, literal_counter = -1):

        # clauses
        if clauses is None:
            self.clauses = {}
        else:
            self.clauses = clauses

        # current assignment for literals
        if current_set_literals is None:
            self.current_set_literals = {}
        else:
            self.current_set_literals = current_set_literals

        # bookkeeping references
        if bookkeeping is None:
            self.bookkeeping = defaultdict(set)
            for clause in clauses.values():
                for literal in clause.literals:
                    self.bookkeeping[abs(literal)].add(clause.id)
        else:
            self.bookkeeping = bookkeeping

        self.literal_counter = literal_counter
        if (literal_counter < 0):
            self.literal_counter = len(self.bookkeeping.keys())

        # counts amount of clauses
        self.clause_counter = clause_counter


    def validate(self) -> Tuple[bool, bool]:
        """
        Determine whether the current knowledge base is solved.
        :return:
        """
        for clause in self.clauses.values():
            solved, _ = clause.validate(self.current_set_literals)
            if not solved:
                return solved, False

        return True, False

    def simplify(self):
        """
        removes redundant information from knowledge base
        """
        self.simplify_unit_clauses()
        self.simplify_pure_literal()

    def simplify_unit_clauses(self):
        """
        simplifies knowledge base for unit clauses
        """
        for clause in list(self.clauses.values()):

            if len(clause.literals) != 1:
                continue

            literal = clause.first()

            valid = self.set_literal(literal, literal > 0)
            if not valid:
                raise Exception("Invalid simplification, should not happen")

    def simplify_pure_literal(self):
        """
        simplifies knowledge base for pure literals
        """
        # Wrap in list call is necessary to not change dict while iterating
        for literal in list(self.bookkeeping.keys()):
            attempt = set()

            for clause_id in self.bookkeeping[literal]:
                if len(attempt) > 1:
                    break
                if literal in self.clauses[clause_id].literals:
                    attempt.add(True)
                elif (-literal) in self.clauses[clause_id].literals:
                    attempt.add(False)

            if len(attempt) == 1:
                value = attempt.pop()
                valid = self.set_literal(literal, value)
                if not valid:
                    raise Exception("Invalid simplification, should not happen")

    def simplify_tautology(self):
        """
        simplifies knowledge base for tautologies clauses
        :return:
        """

        removed = 0
        for clause in list(self.clauses.values()):
            if any((-literal) in clause.literals for literal in clause.literals):
                self.remove_clauses([clause])
                removed += 1

        print(f"Tautology simplify removed {removed} clauses")


    def set_literal(self, literal: int, truth_value: bool) -> bool:
        """
        Set a literal and its boolean value
        :param literal:
        :param truth_value:
        """

        # First check if this is a allowed op.
        literal = abs(literal)

        # Set literal
        self.current_set_literals[literal] = truth_value

        clauses_to_remove = []
        for clause_id in self.bookkeeping[literal]:
            clause = self.clauses[clause_id]

            # If we set P to true and ~P is set, we can remove the clause
            if (not truth_value) and (-literal) in clause.literals:
                clauses_to_remove.append(clause)
            elif truth_value and literal in clause.literals:
                clauses_to_remove.append(clause)
            elif (truth_value is False and literal in clause.literals) or (truth_value is True and (-literal) in clause.literals):

                # Remove empty and satisfied clauses
                if -literal in clause.literals:
                    clause.literals.remove(-literal)
                else:
                    clause.literals.remove(literal)

                if len(clause.literals) == 0:
                    return False

        if literal in self.bookkeeping:
            del self.bookkeeping[literal]

        self.remove_clauses(clauses_to_remove)

        return True


    def remove_clauses(self, clauses_to_remove: List[Clause]):
        """
        Remove list of clauses from KB
        :param clauses_to_remove:
        """
        for clause in clauses_to_remove:
            del self.clauses[clause.id]
            for literal in clause.literals:
                abs_literal = abs(literal)
                if abs_literal not in self.bookkeeping:
                    # This can happen if we remove a tautology forexample
                    continue

                self.bookkeeping[abs_literal].remove(clause.id)
                if len(self.bookkeeping[abs_literal]) == 0:
                    del self.bookkeeping[abs_literal]

    def __str__(self):
        return str({"bookkeeping" : self.bookkeeping, "current_set_literals" : self.current_set_literals, "clause_counter" : self.clause_counter, "clauses" : self.clauses})

    def __repr__(self):
        return self.__str__()

    def split_statistics(self):
        Split = namedtuple('Split', ['literal_cnt', 'clause_cnt'])

        return Split(len(self.bookkeeping.keys()), len(self.clauses))
