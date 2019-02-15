

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

            # split


            # check

            pass

        pass