from copy import deepcopy
from random import choice

from code.knowledge_base import KnowledgeBase


class Solver:


    def __init__(self, knowledge_base):
        self.initial = knowledge_base

    def solve_instance(self):
        """ main function for solving knowledge base """

        # Check tautology (part of simplify, but only done once)
        self.initial.tautology_simplify()

        # init
        # self.initial.insert_rules(instance)
        stack = [self.initial]
        solved = False


        while (not solved):

            # get next element from stack
            current_state = stack.pop(0)

            solved, error = current_state.validate()

            if (solved):

                # found solution
                return current_state

            elif (error):

                continue

            # simplify
            current_state.simplify()

            solved, error = current_state.validate()

            if (solved):

                # found solution
                return current_state

            elif(not error):

                # split

                for future_state in self.possible_moves(current_state):
                    stack.append(future_state)

    def possible_moves(self, current_state : KnowledgeBase) -> list:

        output = []

        for literal in current_state.literal_set:
            for choice in [True, False]:
                if (literal not in current_state.current_truth_values):
                    new_state = deepcopy(current_state)
                    new_state.set_literal(literal, choice)
                    output.append(new_state)
        return output