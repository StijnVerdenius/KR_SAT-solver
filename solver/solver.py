import itertools
from typing import Tuple, List, Generator
from solver.saver import Saver
from solver.knowledge_base import KnowledgeBase
import timeit


class Solver:

    def __init__(self, knowledge_base):
        self.initial = knowledge_base
        self.saver = Saver("./temp/")

    def solve_instance(self) -> Tuple[KnowledgeBase, bool, List]:
        """ main function for solving knowledge base """
        split_statistics = []
        start = timeit.default_timer()
        
        # Check tautology (part of simplify, but only done once)
        self.initial.simplify_tautology()

        stack = iter([self.initial])
        solved = False
        count = 0

        while (not solved):
            count += 1
            # get next entry from stack
            try:
                current_state: KnowledgeBase = next(stack)
                split_statistics.append(current_state.split_statistics())
                # inform user of progress

                runtime = timeit.default_timer() - start

                if count % 25 == 0:
                    count = 1
                    print(f"\rLength solution: {len(current_state.current_set_literals)} out of {current_state.literal_counter} runtime: {runtime}", end='')
            except StopIteration:
                return current_state, False, split_statistics

            # check for solution
            solved, _ = current_state.validate()
            if solved:
                # found solution
                print("\nSolved")
                return current_state, True, split_statistics

            # simplify
            valid = current_state.simplify()
            if not valid:
                continue

            # check again
            solved, _ = current_state.validate()

            if solved:
                # found solution
                print("\nSolved")
                return current_state, True, split_statistics
            else:
                # split
                future_states = self.possible_splits(current_state)
                # stack = self.concat(future_states, stack)
                stack = itertools.chain(future_states, stack)

    def possible_splits(self, current_state: KnowledgeBase) -> Generator[KnowledgeBase, None, None]:
        """
        Generator for possible splits given a current knowledge base and its current truth value assignments

        :param current_state:
        :return:
        """

        for literal in current_state.bookkeeping.keys():
            if literal in current_state.current_set_literals:
                continue

            for choice in [True, False]:
                new_state = self.saver.deepcopy_knowledge_base(current_state)

                # do split
                valid = new_state.set_literal(literal, choice)

                if not valid:
                    # Reached non-valid state, thus leaf-node
                    continue

                yield new_state

    def concat(self, a, b):
        """
        Helper function to concatenate generator outputs

        :param a:
        :param b:
        """

        yield from a
        yield from b



