from collections import defaultdict
from typing import List, Dict, Set, Tuple
from solver.clause import Clause

class KnowledgeBase:

    bookkeeping: Dict[int, Set[int]]
    clauses: Dict[int, Clause]
    current_set_literals: Dict[int, bool]

    def __init__(self, clauses = None, current_set_literals = None, bookeeping = None, counter = 0):

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
        if bookeeping is None:
            self.bookkeeping = defaultdict(set)
            for clause in clauses.values():
                for literal in clause.literals:
                    self.bookkeeping[abs(literal)].add(clause.id)
        else:
            self.bookkeeping = bookeeping

        # counts amount of clauses
        self.clause_counter = counter


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


    # def insert_rules(self, rules):
    #     """ inserts rules to knowledge base """
    #
    #     for rule in rules:
    #         self.clauses.append(Clause(self.clause_counter, rule))
    #         for literal in rule:
    #             self.literal_set.add(literal)
    #             self.bookkeeping[literal].add(self.clause_counter)
    #         self.clause_counter += 1

    def simplify(self):
        self.simplify_unit_clauses()
        self.simplify_pure_literal()

    def simplify_unit_clauses(self):
        for clause in list(self.clauses.values()):
            if clause.length != 1:
                continue

            literal = clause.first()
            valid = self.set_literal(literal, literal > 0)
            if not valid:
                raise Exception("This should not happen")
            # print(f"Simplified unit clause {literal}")

    def simplify_pure_literal(self):
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
                    raise Exception("??")
                print(f"Pure literal: {literal}={value}")

    def tautology_simplify(self):
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
        # for clause_id in self.bookkeeping[literal]:
        #     clause = self.clauses[clause_id]
        #     if len(clause.literals) != 1:
        #         continue
        #     if (truth_value is True and (-literal) in clause.literals) or (truth_value is False and literal in clause.literals):
        #         return False

        # Set literal
        self.current_set_literals[abs(literal)] = truth_value
        clauses_to_remove = []
        for clause_id in self.bookkeeping[literal]:
            clause = self.clauses[clause_id]

            # If we set P to true and ~P is set, we can remove the clause
            if truth_value is False and (-literal) in clause.literals:
                clauses_to_remove.append(clause)
            elif truth_value is True and literal in clause.literals:
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
            # print(f"Removed clause {clause.id}")
            for literal in clause.literals:
                abs_literal = abs(literal)
                if abs_literal not in self.bookkeeping:
                    # This can happen if we remove a tautology
                    continue

                self.bookkeeping[abs_literal].remove(clause.id)
                if len(self.bookkeeping[abs_literal]) == 0:
                    del self.bookkeeping[abs_literal]

                # print(f"Removed bookkeeping[{literal}] => {clause.id}")
