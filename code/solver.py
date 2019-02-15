from copy import deepcopy


class Solver:


    def __init__(self, knowledge_base):
        self.initial = knowledge_base

    def solve_instance(self, instance):
        """ main function for solving knowledge base """

        # init
        self.initial.insert_rules(instance)
        stack = [self.initial]
        solved = False

        while (not solved):

            # get next element from stack
            current_state = stack.pop(0)

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


    def possible_moves(self, current_state):
        output = []

        for literal in current_state.literal_set:
            if (literal not in current_state.current_truth_values):
                new_state = deepcopy(current_state)
                new_state.current_truth_values[literal] =

        return []