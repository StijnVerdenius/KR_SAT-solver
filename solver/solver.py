import itertools
from typing import Tuple, List, Generator, Dict
import operator
from collections import defaultdict
import random
from typing import Tuple, List, Generator
from solver.saver import Saver
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

    def __init__(self, knowledge_base : KnowledgeBase):
        self.initial = knowledge_base
        self.saver = Saver("./temp/")
        self.timestep = 0
        self.clause_counter = self.initial.clause_counter

        self.nr_of_splits = 0
        self.total_literals = knowledge_base.literal_counter
        self.failed_literals = 0

        self.currently_conflict_mode = False
        self.problem_clauses = []
        self.order = ["init"]
        self.stack = {}
        self.restart_limit = 100

        self.cyclefree = defaultdict(int)

    def solve_instance(self) -> Tuple[KnowledgeBase, bool, List]:
        """ main function for solving knowledge base """
        self.nr_of_splits = -1
        split_statistics = []
        start = timeit.default_timer()
        
        # Check tautology (part of simplify, but only done once)
        self.initial.simplify_tautology()

        solved = False
        count = 0

        # to retrieve initial value on start
        current_state = self.saver.deepcopy_knowledge_base(self.initial, 0)
        self.stack["init"] = {True : current_state, False: current_state}

        while (not solved):

            count += 1

            # get next entry from stack
            current_state : KnowledgeBase = self.get_next_state()

            # user & statistics
            count = self.inform_user(current_state, count, start)
            split_statistics.append(current_state.split_statistics())

            # check for solution
            solved, _ = current_state.validate()
            if solved:
                # found solution
                print("\nSolved")
                return current_state, True, split_statistics

            # find set literals before
            before = tuple(current_state.current_set_literals.keys())

            # simplify
            valid, potential_problem = current_state.simplify()

            # find set literals after
            after = tuple(current_state.current_set_literals.keys())

            # add difference to order
            difference = [literal for literal in after if literal not in before]
            for literal in difference:
                self.order.append(literal)
                # todo: ook toevoegen aan stack met simplify-literal refererend naar de voorgaande split-literal ??

            if not valid:
                self.retrieve_problem_clause(current_state, potential_problem)
                continue

            # check again
            solved, _ = current_state.validate()

            if solved:
                # found solution
                print("\nSolved")
                return current_state, True, split_statistics
            else:
                # split
                future_states, literal = self.expand_tree_by_split(current_state)
                self.stack[literal] = future_states

    def retrieve_problem_clause(self, state, literal):

        # up counter
        self.clause_counter += 1

        # get clause
        problem_clause = state.dependency_graph.find_conflict_clause(literal, self.clause_counter)

        # add
        self.problem_clauses.append(problem_clause)

        # trigger a backtrack
        self.currently_conflict_mode = True

    def expand_tree_by_split(self, current_state: KnowledgeBase) -> Tuple[Dict[bool, KnowledgeBase], int]:
        """
        Generator for possible splits given a current knowledge base and its current truth value assignments

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

            new_state = self.saver.deepcopy_knowledge_base(current_state, self.timestep)

            # do split
            valid, potential_problem = new_state.set_literal(literal, truth_assignment, split=True)

            if not valid:

                self.retrieve_problem_clause(new_state, literal)

                continue

            else:

                # problem free
                new_states[truth_assignment] = new_state

        return new_states, literal

    def get_next_state(self) -> KnowledgeBase:

        # if not in error mode: depth first state expansion
        if (not self.currently_conflict_mode):

            self.cyclefree = defaultdict(int)

            # find state values
            # Find the first literal in the order that has a state in the stack
            for last_literal in reversed(self.order):
                 # todo: hearistiek ipv random
                if last_literal in self.stack:
                    break

            truth_assignment = random.choice([True, False])

            # find state
            state = self.saver.deepcopy_knowledge_base(self.stack[last_literal][truth_assignment], -1)

            if (state is None):
                raise Exception("None-state")
                # todo: dit betekent dat in split een fout gaf voor 1 van de twee states en die het somehow overleeft heeft, wat hieraan te doen?

            # add problem clauses
            self.add_problem_clauses_to_state(state)

            return state

        print("Entered backtrack")

        # backtrack
        # reset conflict mode
        self.currently_conflict_mode = False

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
                state = self.saver.deepcopy_knowledge_base(stack_state, stack_state.timestep)
                break

        self.add_problem_clauses_to_state(state)

        # Remove literals that came after from self.order
        after = self.order[order_index + 1:]
        self.order = self.order[:order_index + 1]

        # Remove literals that came after from self.stack
        for literal in after:
            if literal in self.stack:
                del self.stack[literal]

        self.cyclefree[state.timestep] += 1
        if self.cyclefree[state.timestep] > self.restart_limit:
            raise RestartException(f"Max valt op mannen. Also: restart limit of {self.restart_limit} exceeded", restart = True)

        return state


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
            new_state = self.saver.deepcopy_knowledge_base(current_state)
            valid = new_state.set_literal(literal, choice)
            if not valid:
                self.failed_literals += 1
                # Reached non-valid state, thus leaf-node
                return

            yield new_state

    def lookup_backtrack_literal(self, problem_clause):
        for order_index, literal in enumerate(self.order):

            if literal == "init":
                continue

            if abs(literal) in problem_clause.literals:
                if abs(literal) in self.stack:
                    return literal, order_index

                for order_index2 in range(order_index, 0, -1):
                    literal = self.order[order_index2]
                    if literal in self.stack and len(self.stack[literal]):
                        return literal, order_index2

        raise Exception("Could not find backtrack literal")

    def add_problem_clauses_to_state(self, state):
        valid = state.add_clauses(self.saver.personal_deepcopy(self.problem_clauses))
        if (not valid):
            raise Exception("Adding clauses led to invalid addition")


    def inform_user(self, state : KnowledgeBase, count, start):
        # inform user of progress
        if count % 25 == 0:
            runtime = timeit.default_timer() - start
            count = 1
            print(f"\rLength solution: {len(state.current_set_literals)} out of"
                  f" {state.literal_counter}, runtime: {runtime}, number of clauses: "
                  f"{len(state.clauses)}", end='')

        return count


    def nr_of_binary_clauses(self, state):
        return sum((1 for clause in state.clauses.values() if len(clause.literals) == 2))

    def preselect(self, current_state, mu=5, gamma=7):
        items = 0
        n = self.nr_of_splits
        n = max(1, n)
        max_items = int(mu + (gamma / n) + self.failed_literals)
        all_lits = list(current_state.bookkeeping.items())

        print(f"Max items: {max_items}, failed_literals: {self.failed_literals}, total_lits:, nr_of_splits:{self.nr_of_splits}")
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

        return heuristic

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

        print(f"Heuristic len: {len(heuristic)}")
        # Return highest value in heuristic
        if len(heuristic) == 0:
            return [(None, None),]

        literal, heuristic_vals = max(heuristic.items(), key=lambda kv: kv[1][0])
        if heuristic_vals[1] > heuristic_vals[2]:
            return [(literal, True), (literal, False)]
        else:
            return [(literal, False), (literal, True)]