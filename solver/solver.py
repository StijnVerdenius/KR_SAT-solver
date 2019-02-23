import itertools
from typing import Tuple, List, Generator, Dict
import operator
from collections import defaultdict
import random
from typing import Tuple, List, Generator
from solver.data_management import DataManager
from solver.knowledge_base import KnowledgeBase
from solver.clause import Clause
from collections import deque, defaultdict
from solver.restart_exception import RestartException

import random
try:
    import numpy as np
except ImportError:
    raise RuntimeError("Please install numpy")
import timeit


class RunningTimeException(Exception):
    pass


class Solver:

    def __init__(self, knowledge_base : KnowledgeBase, split_stats=None):

        # initial knowledge base
        self.initial = knowledge_base

        # helper for data management
        self.data_manager = DataManager("./temp/")

        # timestep in treesearch
        self.timestep = 0

        # counts clauses
        self.clause_counter = self.initial.clause_counter

        # todo: max
        self.nr_of_splits = 0
        self.total_literals = knowledge_base.literal_counter
        self.failed_literals = 0

        # tracks whether backtrack mode is ctive
        self.backtrack_mode_active = False

        # list of problem clauses
        self.problem_clauses = []

        # keeps track of order tree was expanded for potential backtracking
        self.order = ["init"]

        # keeps stack dictionary to return to right node
        self.stack = {}

        # limit for backtracking back to the same node
        self.backtrack_limit = 25

        # statistics tracker
        if (split_stats == None):
            self.split_statistics = []
        else:
            self.split_statistics = split_stats

        # keeps track of which timestep was backtracked too last
        self.cyclefree = defaultdict(int)

    def solve_instance(self) -> Tuple[KnowledgeBase, bool, List]:
        """
        ##################
        Main solving Function For SAT Solver
        ##################

        :return:
        """

        self.nr_of_splits = -1

        # start timing
        start = timeit.default_timer()
        
        # Check tautology (part of simplify, but only done once)
        self.initial.simplify_tautology()

        solved = False
        count = 0

        # to retrieve initial value on start
        current_state = self.data_manager.duplicate_knowledge_base(self.initial, 0)
        self.stack["init"] = {True : current_state, False: current_state}

        while (not solved):

            count += 1

            # get next entry from stack
            current_state : KnowledgeBase = self.get_next_state()

            # user & statistics
            count = self.inform_user(current_state, count, start)
            self.split_statistics.append(current_state.split_statistics())

            # check for solution
            solved = current_state.validate()
            if solved:
                # found solution
                print("\nSolved")
                return current_state, True, self.split_statistics

            # simplify
            set_literals = []
            valid, potential_problem = current_state.simplify(set_literals)

            # add difference to order
            for literal in set_literals:
                self.order.append(literal)


            if not valid:
                # backtrack
                self.handle_problem_clause(current_state, potential_problem)
                continue

            # check again
            solved = current_state.validate()

            if solved:
                # found solution
                print("\nSolved")
                return current_state, True, self.split_statistics
            else:
                # split
                future_states, literal = self.expand_tree_by_split(current_state)
                self.stack[literal] = future_states

    def handle_problem_clause(self, state, literal):
        """
        Triggers backtracke mode and finds a new problem clause to add to knowledge base

        :param state:
        :param literal:
        :return:
        """

        # up counter
        self.clause_counter += 1

        # get clause
        problem_clause = state.dependency_graph.find_conflict_clause(literal, self.clause_counter)

        # add
        self.problem_clauses.append(problem_clause)

        # trigger a backtrack
        self.backtrack_mode_active = True

    def expand_tree_by_split(self, current_state: KnowledgeBase) -> Tuple[Dict[bool, KnowledgeBase], int]:
        """
        Generator for a splits given a current knowledge base and its current truth value assignments

        :param current_state:
        :return:
        """

        # init with none
        new_states = {True: None, False: None}

        self.timestep += 1

        # choose a literal todo: heuristiek ipv random
        literal = random.choice(list(current_state.bookkeeping.keys()))
        while literal in current_state.current_set_literals:
            literal = random.choice(list(current_state.bookkeeping.keys()))

        # add literal to order
        self.order.append(literal)

        for truth_assignment in [False, True]:

            new_state = self.data_manager.duplicate_knowledge_base(current_state, self.timestep)

            # do split
            valid, potential_problem = new_state.set_literal(literal, truth_assignment, split=True)

            if not valid:

                self.handle_problem_clause(new_state, literal)

                continue

            else:

                # problem free
                new_states[truth_assignment] = new_state

        return new_states, literal

    def get_next_state(self) -> KnowledgeBase:
        """
        Gets the next state.
        Does backtracking if needed

        :return:
        """

        # if not in error mode: depth first state expansion
        if (not self.backtrack_mode_active):

            # reset infinite loop detection
            self.cyclefree = defaultdict(int)

            # find state values
            # Find the first literal in the order that has a state in the stack
            for last_literal in reversed(self.order):
                if last_literal in self.stack:
                    break

            truth_assignment = random.choice([True, False])

            # find state
            state = self.stack[last_literal][truth_assignment]
            state = self.data_manager.duplicate_knowledge_base(state, state.timestep)

            # add problem clauses
            self.add_problem_clauses_to_state(state)

            return state

        else: # backtrack

            # reset conflict mode
            self.backtrack_mode_active = False

            # find relevant problem clause
            problem_clause: Clause = self.problem_clauses[-1]

            # Find earliest literal from problem clause in order and stack
            literal, order_index = self.lookup_backtrack_literal(problem_clause)

            # Find corresponding state in stack
            possible_assignments = [False, True]
            random.shuffle(possible_assignments)
            for truth_assignment in possible_assignments:
                if truth_assignment in self.stack[literal]:
                    stack_state : KnowledgeBase = self.stack[literal][truth_assignment]
                    state = self.data_manager.duplicate_knowledge_base(stack_state, stack_state.timestep)
                    break

            self.add_problem_clauses_to_state(state)

            # Remove literals that came after from self.order
            after = self.order[order_index + 1:]
            self.order = self.order[:order_index + 1]

            # Remove literals that came after from self.stack
            for literal in after:
                if literal in self.stack:
                    del self.stack[literal]

            # check if stuck in a loop
            self.cyclefree[state.timestep] += 1
            if (self.cyclefree[state.timestep] > self.backtrack_limit):

                # restart if so
                raise RestartException(f"\nBacktrack limit of {self.backtrack_limit} exceeded, attempting restart", restart = True, stats=self.split_statistics)

            return state


    def lookup_backtrack_literal(self, problem_clause):
        """
        Finds node to backtrack to given a problem clause that has arisen after conflict

        :param problem_clause:
        :return:
        """

        for order_index, literal in enumerate(self.order):

            if literal == "init":
                continue

            if abs(literal) in problem_clause.literals:
                if abs(literal) in self.stack:
                    return abs(literal), order_index

                for order_index2 in range(order_index, 0, -1):
                    literal = self.order[order_index2]
                    if literal in self.stack and len(self.stack[literal]):
                        return literal, order_index2

        raise RestartException("Could not find backtrack literal!", restart=True, stats=self.split_statistics)

    def add_problem_clauses_to_state(self, state):
        """
        Adds list of discovered problem clauses to new state

        :param state:
        :return:
        """
        valid = state.add_clauses(self.data_manager.personal_deepcopy(self.problem_clauses))
        if (not valid):
            raise RestartException("Adding clauses led to invalid addition!", restart=True, stats=self.split_statistics)


    def inform_user(self, state : KnowledgeBase, count, start):
        """ Log to user if it takes long """

        # inform user of progress
        if count % 25 == 0:
            runtime = timeit.default_timer() - start
            count = 1
            print(f"\rLength solution: {len(state.current_set_literals)} out of"
                  f" {state.literal_counter}, runtime: {runtime}, number of clauses: "
                  f"{len(state.clauses)}", end='')

        return count


    # def nr_of_binary_clauses(self, state):
    #     return sum((1 for clause in state.clauses.values() if len(clause.literals) == 2))
    #
    # def preselect(self, current_state, mu=5, gamma=7):
    #     items = 0
    #     n = self.nr_of_splits
    #     n = max(1, n)
    #     max_items = int(mu + (gamma / n) + self.failed_literals)
    #     all_lits = list(current_state.bookkeeping.items())
    #
    #     print(f"Max items: {max_items}, failed_literals: {self.failed_literals}, total_lits:, nr_of_splits:{self.nr_of_splits}")
    #     # allowed_lits = list(set(current_state.bookkeeping.keys()))
    #     # random.shuffle(allowed_lits)
    #     # for literal in allowed_lits:
    #     for literal, _ in sorted(all_lits, key=lambda kv: len(kv[1])):
    #         if literal in current_state.current_set_literals:
    #             continue
    #
    #         yield literal
    #
    #         items += 1
    #         if items == max_items and self.nr_of_splits > 1:
    #             break
    #
    # def diff(self, state, new_state):
    #     # Clause reduction heuristic
    #     gammas = {2: 1, 3: 0.2, 4: 0.05, 5: 0.01, 6: 0.003}
    #     for k in range(7, 10):
    #         gammas[k] = 20.4514 * 0.218673 ** k
    #
    #
    #     count_dict_state = defaultdict(int)
    #     for clause in state.clauses.values():
    #         count_dict_state[len(clause)] += 1
    #
    #     count_dict_new_state = defaultdict(int)
    #     for clause in new_state.clauses.values():
    #         count_dict_new_state[len(clause)] += 1
    #
    #     heuristic = sum(abs(count_dict_new_state[k] - count_dict_state[k]) * gammas[k] for k in range(2, 10))
    #
    #     return heuristic
    #
    # def double_look(self, current_state):
    #     f = current_state
    #     for literal in self.preselect(current_state):
    #         fprime = self.data_manager.duplicate_knowledge_base(current_state)
    #         valid1 = fprime.set_literal(literal, False)
    #         if valid1:
    #             valid1 = fprime.simplify()
    #
    #         fdprime = self.data_manager.duplicate_knowledge_base(current_state)
    #         valid2 = fdprime.set_literal(literal, True)
    #         if valid2:
    #             valid2 = fdprime.simplify()
    #
    #         if not valid1 and not valid2:
    #             return fprime, False
    #         elif not valid1:
    #             f = fdprime
    #         elif not valid2:
    #             f = fprime
    #
    #     return f, True
    #
    # def look_ahead(self, current_state):
    #     heuristic = {}
    #     f = current_state
    #     for literal in self.preselect(current_state):
    #         fprime = self.data_manager.duplicate_knowledge_base(current_state, current_state.timestep)
    #         valid1 = fprime.set_literal(literal, False)
    #         if valid1:
    #             valid1 = fprime.simplify()
    #
    #         if valid1 and self.nr_of_binary_clauses(fprime) - 65 > self.nr_of_binary_clauses(f):
    #             fprime, valid1 = self.double_look(fprime)
    #
    #         fdprime = self.data_manager.duplicate_knowledge_base(current_state)
    #         valid2 = fdprime.set_literal(literal, True)
    #         if valid2:
    #             valid2 = fdprime.simplify()
    #
    #         if valid2 and self.nr_of_binary_clauses(fdprime) - 65 > self.nr_of_binary_clauses(f):
    #             fdprime, valid2 = self.double_look(fdprime)
    #
    #         if not valid1 and not valid2:
    #             return [(None, None),]
    #         elif not valid1:
    #             self.failed_literals += 1
    #             f = fdprime
    #         elif not valid2:
    #             self.failed_literals += 1
    #             f = fprime
    #         else:
    #             diff_fd_prime = self.diff(f, fdprime)
    #             diff_f_prime = self.diff(f, fprime)
    #             heuristic[literal] = (
    #                 1024 * diff_f_prime * diff_fd_prime + diff_f_prime + diff_fd_prime,
    #                 diff_fd_prime,
    #                 diff_f_prime,
    #             )
    #
    #     # print(f"Heuristic len: {len(heuristic)}")
    #     # Return highest value in heuristic
    #     if len(heuristic) == 0:
    #         return [(None, None),]
    #
    #     literal, heuristic_vals = max(heuristic.items(), key=lambda kv: kv[1][0])
    #     if heuristic_vals[1] > heuristic_vals[2]:
    #         return [(literal, True), (literal, False)]
    #     else:
    #         return [(literal, False), (literal, True)]
    #
    #
    # def possible_splits(self, current_state: KnowledgeBase) -> Generator[KnowledgeBase, None, None]:
    #     """
    #     Generator for possible splits given a current knowledge base and its current truth value assignments
    #
    #     :param current_state:
    #     :return:
    #     """
    #     set_literals = set()
    #     iterator = self.look_ahead(current_state)
    #
    #     for literal, choice in iterator:
    #         if literal is None:
    #             solved, _ = current_state.validate()
    #             if solved:
    #                 raise Exception("LoL")
    #             # print("Returning")
    #             return
    #
    #         # for choice in [True, False]:
    #         # print(f"Choice: {literal}={choice}")
    #
    #         # do split
    #         new_state = self.data_manager.duplicate_knowledge_base(current_state)
    #         valid = new_state.set_literal(literal, choice)
    #         if not valid:
    #             self.failed_literals += 1
    #             # Reached non-valid state, thus leaf-node
    #             return
    #
    #         yield new_state