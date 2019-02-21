from collections import defaultdict, namedtuple
from typing import List, Dict, Set, Tuple
from solver.clause import Clause
from solver.dependency_graph import DependencyGraph

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
    dependency_graph : DependencyGraph


    def __init__(self, clauses = None, current_set_literals = None, bookkeeping = None, clause_counter = 0, literal_counter = -1, dependency_graph = None, timestep=0):

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

        if dependency_graph == None:
            self.dependency_graph = DependencyGraph(bookkeeping=self.bookkeeping, clauses = self.clauses)
        else:
            self.dependency_graph = dependency_graph

        self.timestep = timestep


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

    def simplify(self) -> Tuple[bool, int]:
        """
        removes redundant information from knowledge base
        """
        valid, potential_problem = self.simplify_unit_clauses()
        if not valid:
            return valid, potential_problem
        # valid = self.simplify_pure_literal()
        if not valid:
            return valid, potential_problem

        return True, 0

    def simplify_unit_clauses(self):
        """
        simplifies knowledge base for unit clauses
        """
        for clause in list(self.clauses.values()):

            if len(clause.literals) != 1:
                continue

            literal = clause.first()

            truth_value = literal > 0
            valid, potential_problem = self.set_literal(literal, truth_value)
            if not valid:
                return valid, potential_problem

        return True, 0

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
                valid, potential_problem = self.set_literal(literal, value)
                if not valid:
                    return valid, potential_problem

        return True, 0

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


    def set_literal(self, literal: int, truth_value: bool) -> Tuple[bool, int]:
        """
        Set a literal and its boolean value
        :param literal:
        :param truth_value:
        """

        # print(f"set {literal} to {truth_value}")

        # First check if this is a allowed op.
        abs_literal = abs(literal)

        self.dependency_graph.add_literal(abs_literal)

        # Set literal
        self.current_set_literals[abs_literal] = truth_value

        clauses_to_remove = []
        for clause_id in self.bookkeeping[abs_literal]:
            clause = self.clauses[clause_id]

            # If we set P to true and ~P is set, we can remove the clause
            if (not truth_value) and (-abs_literal) in clause.literals:
                clauses_to_remove.append(clause)
            elif truth_value and abs_literal in clause.literals:
                clauses_to_remove.append(clause)
            else:
                #(truth_value is False and literal in clause.literals) or (truth_value is True and (-literal) in clause.literals):
                if len(clause.literals) == 1:
                    return False, abs_literal

                # Remove empty and satisfied clauses
                if -abs_literal in clause.literals:
                    clause.literals.remove(-abs_literal)
                if abs_literal in clause.literals:
                    clause.literals.remove(abs_literal)


        if abs_literal in self.bookkeeping:
            del self.bookkeeping[abs_literal]

        self.remove_clauses(clauses_to_remove)

        return True, abs_literal


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

    def add_clauses(self, clauses: Set[Clause]):
        going_strong = True
        for clause in clauses:
            if (clause.id not in self.clauses):
                going_strong = self.add_clause(clause)
                if not going_strong:
                    break
            else:
                raise Exception("Clause id not unique")
        return going_strong

    def add_clause(self, clause: Clause):
        literals = clause.literals
        id = clause.id

        for literal in list(literals):

            # is literal already set
            abs_literal = abs(literal)
            if (abs_literal in self.current_set_literals):
                truth = self.current_set_literals[abs_literal]

                # is it already statiusfied?
                if (literal> 0 and truth or (literal<0 and not truth)):
                    return True
                else:
                    # remove literal from clause
                    literals.remove(literal)

        # if empty: conflict
        if (len(literals) == 0):
            return False

        # adding
        for literal in literals:
            self.bookkeeping[abs(literal)].add(id)
        self.clauses[id] = clause
        self.clause_counter += 1
        return True
