from copy import deepcopy
from random import choice
from typing import Tuple, List, Generator



from solver.knowledge_base import KnowledgeBase


def concat(a, b):
    yield from a
    yield from b


class Solver:


    def __init__(self, knowledge_base):
        self.initial = knowledge_base

    def solve_instance(self) -> Tuple[KnowledgeBase, bool]:
        """ main function for solving knowledge base """

        # Check tautology (part of simplify, but only done once)
        self.initial.tautology_simplify()

        # init
        # self.initial.insert_rules(instance)
        stack = iter([self.initial])
        solved = False


        while (not solved):
            # if len(stack) == 0:
            #      return current_state, False
            try:
                current_state = next(stack)
            except StopIteration:
                return current_state, False

            # get next element from stack
            # current_state = stack.pop()
            # print(f"Stack size: {len(stack)}")

            solved, _ = current_state.validate()

            if solved:
                # found solution
                print("Solved")
                return current_state, True


            # simplify
            current_state.simplify()

            solved, _ = current_state.validate()

            if solved:
                # found solution
                print("Solved")
                return current_state, True
            # elif not error:
            else:
                print("splitting")
                # split
                future_states = self.possible_moves(current_state)
                stack = concat(future_states, stack)
                # for future_state in self.possible_moves(current_state):
                #     stack.append(future_state)

    def possible_moves(self, current_state : KnowledgeBase) -> Generator[KnowledgeBase, None, None]:
        # output = []
        for literal in list(current_state.bookkeeping.keys()):
            if literal in current_state.current_set_literals:
                continue

            for choice in [True, False]:
                new_state = deepcopy(current_state)
                valid = new_state.set_literal(literal, choice)
                if not valid:
                    print("Reached non-valid state, end-of-tree")
                    continue

                # output.append(new_state)
                yield new_state

        # print(f"Generated possible moves {len(output)}")
        # return output
