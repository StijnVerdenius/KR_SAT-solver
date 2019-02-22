import itertools
import operator
from collections import defaultdict
import random
from typing import Tuple, List, Generator
from solver.saver import Saver
from solver.knowledge_base import KnowledgeBase
import timeit


class RunningTimeException(Exception):
    pass


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

                runtime = timeit.default_timer() - start
                if runtime > 30:
                    raise RunningTimeException(f"!!! SKIPPING SUDOKU. Time is out, runtime:{runtime} !!!")
                    pass

                if count % 1 == 0:
                    count = 1
                    print(f"\rLength solution: {len(current_state.current_set_literals)} out of {current_state.literal_counter} runtime: {runtime}", end='')
            except StopIteration:
                raise Exception("Sudoku solving failed")
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
        set_literals = set()
        iterator = self.look_ahead(current_state)

        for literal, choice in iterator:
            if literal is None:
                solved, _ = current_state.validate()
                if solved:
                    raise Exception("LoL")
                # print("Returning")
                return

            # for choice in [True, False]:
            # print(f"Choice: {literal}={choice}")

            # do split
            new_state = self.saver.deepcopy_knowledge_base(new_state)
            valid = new_state.set_literal(literal, choice)
            if not valid:
                self.failed_literals += 1
                # Reached non-valid state, thus leaf-node
                return

            yield new_state

    def look_ahead(self, current_state):
        heuristic = {}
        f = current_state
        for literal in self.preselect(current_state):
            fprime = self.saver.deepcopy_knowledge_base(current_state)
            valid1 = fprime.set_literal(literal, False)
            if valid1:
                valid1 = fprime.simplify()

            if valid1 and self.nr_of_binary_clauses(fprime) - 65 > self.nr_of_binary_clauses(f):
                fprime, valid1 = self.double_look(fprime)

            fdprime = self.saver.deepcopy_knowledge_base(current_state)
            valid2 = fdprime.set_literal(literal, True)
            if valid2:
                valid2 = fdprime.simplify()

            if valid2 and self.nr_of_binary_clauses(fdprime) - 65 > self.nr_of_binary_clauses(f):
                fdprime, valid2 = self.double_look(fdprime)

            if not valid1 and not valid2:
                return [(None, None),]
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

        # print(heuristic)
        # print(f"Heuristic len: {len(heuristic)}")
        # Return highest value in heuristic
        if len(heuristic) == 0:
            # print(f"Restarting look ahead!!!!")
            # count_dict = defaultdict(int)
            # for clause in current_state.clauses.values():
            #     count_dict[len(clause)] += 1
            #
            # print(count_dict)
            return [(None, None),]
            # self.look_ahead(current_state)

        literal, heuristic_vals = max(heuristic.items(), key=lambda kv: kv[1][0])
        if heuristic_vals[1] > heuristic_vals[2]:
            return [(literal, True), (literal, False)]
        else:
            return [(literal, False), (literal, True)]

    def double_look(self, current_state):
        f = current_state
        for literal in self.preselect(current_state):
            fprime = self.saver.deepcopy_knowledge_base(current_state)
            valid1 = fprime.set_literal(literal, False)
            if valid1:
                valid1 = fprime.simplify()

            fdprime = self.saver.deepcopy_knowledge_base(current_state)
            valid2 = fdprime.set_literal(literal, True)
            if valid2:
                valid2 = fdprime.simplify()

            if not valid1 and not valid2:
                return fprime, False
            elif not valid1:
                f = fdprime
            elif not valid2:
                f = fprime

        return f, True

    def diff(self, state, new_state):
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

        # all_lits = [clause.literals for clause in state.clauses.values()]
        # for clause in new_state.clauses.values():
        #     if clause.literals in all_lits:
        #         k = len(clause.literals)
        #         if k in gammas:
        #             gamma = gammas[k]
        #         else:
        #             gamma = 20.4514 * 0.218673 ** k
        #
        #         sum += gamma * 1

        # nr_clauses = sum((1 for clause in state.clauses.values() if len(clause.literals) == 2))
        # nr_clauses_other = sum((1 for clause in new_state.clauses.values() if len(clause.literals) == 2))

        # nr_clauses = len(state.clauses)
        # nr_clauses_other = len(new_state.clauses)
        # heur = nr_clauses_other - nr_clauses

        return heuristic

    def preselect(self, current_state, mu=5, gamma=7):
        items = 0
        n = self.nr_of_splits
        n = max(1, n)
        max_items = int(mu + (gamma / n) + self.failed_literals)
        all_lits = list(current_state.bookkeeping.items())

        # print(f"Max items: {max_items}, failed_literals: {self.failed_literals}, total_lits:, nr_of_splits:{self.nr_of_splits}")
        # allowed_lits = list(set(current_state.bookkeeping.keys()))
        # random.shuffle(allowed_lits)
        # for literal in allowed_lits:
        for literal, _ in sorted(all_lits, key=lambda kv: len(kv[1])):
            if literal in current_state.current_set_literals:
                continue

            yield literal

            items += 1
            if items == max_items and self.nr_of_splits > 1:
                break


    def concat(self, a, b):
        """
        Helper function to concatenate generator outputs

        :param a:
        :param b:
        """

        yield from a
        yield from b

    def nr_of_binary_clauses(self, state):
        return sum((1 for clause in state.clauses.values() if len(clause.literals) == 2))







