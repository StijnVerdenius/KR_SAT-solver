import itertools
import operator
from collections import defaultdict
import random
from typing import Tuple, List, Generator

from solver.data_management import DataManager
from solver.knowledge_base import KnowledgeBase
import timeit


class LookAHeadSolver:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.initial = knowledge_base
        self.saver = DataManager("./temp/")
        self.nr_of_splits = 0
        self.total_literals = knowledge_base.literal_counter
        self.failed_literals = 0
        self.start = 0

    def get_elapsed_runtime(self):
        return timeit.default_timer() - self.start

    def solve_instance(self) -> Tuple[KnowledgeBase, bool, List]:
        """ main function for solving knowledge base """
        self.nr_of_splits = -1
        self.split_statistics = []
        self.start = timeit.default_timer()

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
                # inform user of progress

                runtime = timeit.default_timer() - self.start
                if runtime > 30:
                    # raise RunningTimeException(f"!!! SKIPPING SUDOKU. Time is out, runtime:{runtime} !!!")
                    pass

                if count % 1 == 0:
                    count = 1
                    print(f"\rLength solution: {len(current_state.current_set_literals)} out of {current_state.literal_counter} runtime: {runtime}", end='')
            except StopIteration:
                raise Exception("Sudoku solving failed")
                return current_state, False, self.split_statistics

            # check for solution
            solved = current_state.validate()
            if solved:
                # found solution
                print("\nSolved")
                return current_state, True, self.split_statistics
            self.split_statistics.append(current_state.split_statistics(self.get_elapsed_runtime()))

            # simplify
            valid = current_state.simplify([], False)
            if not valid:
                continue

            # check again
            solved = current_state.validate()

            if solved:
                # found solution
                print("\nSolved")
                return current_state, True, self.split_statistics
            else:
                # split
                future_states = self.split(current_state)
                stack = itertools.chain(future_states, stack)

    def split(self, current_state: KnowledgeBase) -> Generator[KnowledgeBase, None, None]:
        """
        Splits current state with values {False, True}, for a certain literal

        :param current_state:
        :return:
        """
        iterator = self.look_ahead(current_state)
        for new_state, literal, choice in iterator:
            if literal is None or new_state is None:
                return
            current_state: KnowledgeBase = new_state

            # do split
            new_state = self.saver.duplicate_knowledge_base(current_state, -1, False)
            valid = new_state.set_literal(literal, choice)[0]
            if not valid:
                self.failed_literals += 1
                # Reached non-valid state, thus leaf-node
                return

            yield new_state

    def look_ahead(self, current_state):
        """
        Look ahead of the current state
        And set any forced literals
        Returns the most promising branch according to a heuristic
        :param current_state:
        :return:
        """
        heuristic = {}
        f: KnowledgeBase = current_state
        for literal in self.preselect(f):
            # if literal in f.current_set_literals:
            #     continue

            fprime = self.saver.duplicate_knowledge_base(f, -1, False)
            valid1 = fprime.set_literal(literal, False)[0]
            if valid1:
                valid1 = fprime.simplify([], False)[0]
            self.split_statistics.append(fprime.split_statistics(self.get_elapsed_runtime()))

            if valid1 and fprime.nr_of_binary_clauses() - 65 > f.nr_of_binary_clauses():
                fprime, valid1 = self.double_look(fprime)

            fdprime = self.saver.duplicate_knowledge_base(f, -1, False)
            valid2 = fdprime.set_literal(literal, True)[0]
            if valid2:
                valid2 = fdprime.simplify([], False)[0]
            self.split_statistics.append(fdprime.split_statistics(self.get_elapsed_runtime()))

            if valid2 and fdprime.nr_of_binary_clauses() - 65 > f.nr_of_binary_clauses():
                fdprime, valid2 = self.double_look(fdprime)

            if not valid1 and not valid2:
                return [(None, None, None),]
            elif not valid1:
                self.failed_literals += 1
                f = fdprime
            elif not valid2:
                self.failed_literals += 1
                f = fprime
            else:
                diff_fd_prime = self.diff(f, fdprime)
                diff_f_prime = self.diff(f, fprime)
                heuristic[literal] = (
                    1024 * diff_f_prime * diff_fd_prime + diff_f_prime + diff_fd_prime,
                    diff_fd_prime,
                    diff_f_prime,
                )

        if len(heuristic) == 0:
            return [(None, None, None),]

        literal, heuristic_vals = max(heuristic.items(), key=lambda kv: kv[1][0])
        if heuristic_vals[1] > heuristic_vals[2]:
            return [(f, literal, True), (f, literal, False)]
        else:
            return [(f, literal, False), (f, literal, True)]

    def double_look(self, current_state):
        """
        Look ahead of the current state again, and set any forced literals.
        :param current_state:
        :return:
        """
        f = current_state
        for literal in self.preselect(current_state):
            if literal in f.current_set_literals:
                continue

            fprime = self.saver.duplicate_knowledge_base(f, -1, False)
            valid1 = fprime.set_literal(literal, False)[0]
            if valid1:
                valid1 = fprime.simplify([], False)[0]
            self.split_statistics.append(fprime.split_statistics(self.get_elapsed_runtime()))

            fdprime = self.saver.duplicate_knowledge_base(f, -1, False)
            valid2 = fdprime.set_literal(literal, True)[0]
            if valid2:
                valid2 = fdprime.simplify([], False)[0]
            self.split_statistics.append(fdprime.split_statistics(self.get_elapsed_runtime()))

            if not valid1 and not valid2:
                return fprime, False
            elif not valid1:
                f = fdprime
            elif not valid2:
                f = fprime

        return f, True

    def diff(self, state, new_state):
        """
        Returns a heuristic value by comparing two states, implements Clause reduction heuristic (CRH).
        A higher heuristic value means this state is more promising.
        """
        # Clause reduction heuristic
        gammas = {2: 1, 3: 0.2, 4: 0.05, 5: 0.01, 6: 0.003}
        for k in range(7, 10):
            gammas[k] = 20.4514 * 0.218673 ** k


        count_dict_state = defaultdict(int)
        for clause in state.clauses.values():
            count_dict_state[len(clause)] += 1

        count_dict_new_state = defaultdict(int)
        for clause in new_state.clauses.values():
            count_dict_new_state[len(clause)] += 1

        heuristic = sum(abs(count_dict_new_state[k] - count_dict_state[k]) * gammas[k] for k in range(2, 10))

        return heuristic

    def preselect(self, current_state, mu=5, gamma=7):
        """
        Return a set of P literals, returns a maximum amount of literals max_items
        Literals returned are the literals that have the most occurrences in all clauses.
        :param current_state:
        :param mu: The minimum number of literals returned (if so many are not yet set)
        :param gamma: Determines how heavy to factor in the amount of splits done so far.
        """
        items = 0
        n = self.nr_of_splits
        n = max(1, n)
        max_items = int(mu + (gamma / n) + self.failed_literals)
        all_lits = list(current_state.bookkeeping.items())

        for literal, _ in sorted(all_lits, key=lambda kv: len(kv[1])):
            if literal in current_state.current_set_literals:
                continue

            yield literal

            items += 1
            if items == max_items:
                break
