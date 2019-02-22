import itertools
import operator
from typing import Tuple, List, Generator
from solver.saver import Saver
from solver.knowledge_base import KnowledgeBase
import timeit





class Solver:

    def __init__(self, knowledge_base: KnowledgeBase):
        self.initial = knowledge_base
        self.saver = Saver("./temp/")
        self.nr_of_splits = 0
        self.total_literals = knowledge_base.literal_counter
        self.failed_literals = 0

    def solve_instance(self) -> Tuple[KnowledgeBase, bool, List]:
        """ main function for solving knowledge base """
        self.nr_of_splits = -1
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
                self.nr_of_splits += 1
                split_statistics.append(current_state.split_statistics())
                # inform user of progress


                if count % 10 == 0:
                    runtime = timeit.default_timer() - start
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

            literal, choice = self.look_ahead(current_state)
            if literal is None:
                return

            # for choice in [True, False]:
            new_state = self.saver.deepcopy_knowledge_base(current_state)

            # do split
            valid = new_state.set_literal(literal, choice)
            if not valid:
                self.failed_literals += 1
                # Reached non-valid state, thus leaf-node
                return

            yield new_state
            yield from self.possible_splits(current_state)


    def look_ahead(self, current_state):
        heuristic = {}
        f = current_state
        for literal in self.preselect(current_state):
            fprime = self.saver.deepcopy_knowledge_base(current_state)
            fprime.set_literal(literal, False)
            valid1 = fprime.simplify()

            fdprime = self.saver.deepcopy_knowledge_base(current_state)
            fdprime.set_literal(literal, True)
            valid2 = fdprime.simplify()

            if not valid1:
                self.failed_literals += 1
                f = fdprime
            elif not valid2:
                self.failed_literals += 1
                f = fprime
            else:
                heuristic[literal] = (
                    1024 * self.diff(f, fprime) * self.diff(f, fdprime) + self.diff(f, fprime) + self.diff(f, fdprime),
                    self.diff(f, fdprime),
                    self.diff(f, fprime),
                )

        # Return highest value in heuristic
        if len(heuristic) == 0:
            print(f"Restarting look ahead!!!!")
            return None, None
            # self.look_ahead(current_state)

        literal, heuristic_vals = max(heuristic.items(), key=lambda kv: kv[1][0])
        if heuristic_vals[1] > heuristic_vals[2]:
            return literal, True
        else:
            return literal, False


    def diff(self, state, new_state):
        # nr_clauses = sum((1 for clause in state.clauses.values() if len(clause.literals) == 2))
        nr_clauses = len(state.clauses)
        # nr_clauses_other = sum((1 for clause in new_state.clauses.values() if len(clause.literals) == 2))
        nr_clauses_other = len(new_state.clauses)

        return abs(nr_clauses_other - nr_clauses)

    def preselect(self, current_state, mu=5, gamma=7):
        items = 0
        n = self.nr_of_splits
        n = max(1, n)
        max_items = int(mu + (gamma / n) + self.failed_literals)
        print(f"Max items: {max_items}, failed_literals: {self.failed_literals}")
        for literal, _ in sorted(current_state.bookkeeping.items(), key=lambda kv: len(kv[1])):
            if literal in current_state.current_set_literals:
                continue

            yield literal

            items += 1
            if items == max_items and self.nr_of_splits != 0:
                break


    def concat(self, a, b):
        """
        Helper function to concatenate generator outputs

        :param a:
        :param b:
        """

        yield from a
        yield from b







