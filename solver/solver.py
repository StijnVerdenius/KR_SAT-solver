from copy import deepcopy
from typing import Tuple, List, Generator

from solver.saver import Saver
from solver.clause import Clause
from solver.knowledge_base import KnowledgeBase


def concat(a, b):
    yield from a
    yield from b


class Solver:

    def __init__(self, knowledge_base):
        self.initial = knowledge_base
        self.saver = Saver("./temp/")

    def solve_instance(self) -> Tuple[KnowledgeBase, bool]:
        """ main function for solving knowledge base """

        # Check tautology (part of simplify, but only done once)
        self.initial.simplify_tautology()

        # init
        # self.initial.insert_rules(instance)
        stack = iter([self.initial])
        # stack = [self.initial]
        solved = False

        while (not solved):
            # if len(stack) == 0:
            #      return current_state, False
            try:
                current_state = next(stack)
                print(f"\rLength solution: {len(current_state.current_set_literals)}", end='')
                if (len(current_state.current_set_literals) > 100):
                    print("start")
                    raise StopIteration ## test
            except StopIteration:
                return current_state, False

            # get next element from stack
            # current_state = stack.pop()
            # print(f"Stack size: {len(stack)}")

            solved, _ = current_state.validate()

            if solved:
                # found solution
                print("\nSolved")
                return current_state, True

            # simplify
            current_state.simplify()

            solved, _ = current_state.validate()

            if solved:
                # found solution
                print("\nSolved")
                return current_state, True
            # elif not error:
            else:
                # print("splitting")
                # split
                future_states = self.possible_moves(current_state)
                stack = concat(future_states, stack)
                # for future_state in self.possible_moves(current_state):
                #     stack.append(future_state)

    def possible_moves(self, current_state: KnowledgeBase) -> Generator[KnowledgeBase, None, None]:
        # output = []
        for literal in list(current_state.bookkeeping.keys()):

            if literal in current_state.current_set_literals:
                continue

            for choice in [True, False]:

                new_state = self.saver.deepcopy_kb(current_state)
                # new_state = self.saver.personal_deepcopy(current_state)

                valid = new_state.set_literal(literal, choice)

                # print(f"Choice {literal}={choice}")
                if not valid:
                    # print("Reached non-valid state, end-of-tree")
                    continue

                # output.append(new_state)
                yield new_state

        # print(f"Generated possible moves {len(output)}")
        # return output

def test_solver_tautology():
    clauses = {1: Clause(1, [1, 2, 3, -1])}
    kb = KnowledgeBase(clauses, counter=1)
    s = Solver(kb)

    assert s.solve_instance()[1] is True


def test_solver_diplomatic_puzzle():
    clauses = {1: Clause(1, [1, -2]), 2: Clause(2, [2, 3]), 3: Clause(3, [-3, -1])}
    kb = KnowledgeBase(clauses, counter=3)
    s = Solver(kb)

    res, solved = s.solve_instance()

    assert res.current_set_literals == {1:True, 2: True, 3: False}
    assert solved is True

def test_solver_case3():

    clauses = [Clause(1, [1, -2]), Clause(2, [1, -3, 2]), Clause(3, [3, 2, -1]), Clause(4, [-2, -1, 3])]
    clauses = {clause.id: clause for clause in clauses}
    kb = KnowledgeBase(clauses, counter=3)
    s = Solver(kb)

    res, solved = s.solve_instance()

    # assert res.current_set_literals == {1:True, 2: True, 3: True}
    # assert solved is True