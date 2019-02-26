from typing import Tuple, List, Dict
from implementation.solver.knowledge_base import KnowledgeBase
from implementation.model.clause import Clause
from collections import defaultdict
from implementation.model.exception_implementations import RestartException
from implementation.solver.solver import Solver
import random
try:
    import numpy as np
except ImportError:
    raise RuntimeError("Please install numpy")
import timeit

class CDCL_DPLL_Solver(Solver):

    """
    Implements both CDCL and standard DPLL solving

    """

    def __init__(self, knowledge_base: KnowledgeBase, split_stats=None, heuristics=None, problem_id=None, start=None):

        super().__init__(knowledge_base, problem_id)

        if (heuristics == None):
            raise Exception("No heuristics specified")
        else:
            self.heuristics = heuristics

        # timestep in treesearch
        self.timestep = 0

        # counts clauses
        self.clause_counter = self.initial.clause_counter

        # tracks whether backtrack mode is ctive
        self.backtrack_mode_active = False

        # list of problem clauses
        self.problem_clauses = []

        # keeps track of order tree was expanded for potential backtracking
        self.order = ["init"]

        # keeps stack dictionary to return to right node
        self.stack = {}

        # limit for backtracking back to the same node
        self.backtrack_limit = 30

        # statistics tracker
        if (split_stats == None):
            self.split_statistics = []
        else:
            self.split_statistics = split_stats

        # keeps track of which timestep was backtracked too last
        self.cyclefree = defaultdict(int)

        self.start = start



    def solve_instance(self) -> Tuple[KnowledgeBase, bool, List]:
        """
        ##################
        Main solving Function For SAT Solver
        ##################

        :return:
        """

        self.nr_of_splits = -1

        # start timing
        if (self.start is None):
            self.start = timeit.default_timer()
        
        # Check tautology (part of simplify, but only done once)
        self.initial.simplify_tautology()

        solved = False
        count = 0

        # to retrieve initial value on start
        current_state = self.data_manager.duplicate_knowledge_base(self.initial, 0, use_dependency_graph=self.is_dependency_graph_active())
        self.stack["init"] = {True : current_state, False: current_state}

        while (not solved):

            count += 1

            # get next entry from stack
            current_state : KnowledgeBase = self.get_next_state()

            # user & statistics
            count = self.inform_user(current_state, count, self.start)
            self.split_statistics.append(current_state.split_statistics(self.get_elapsed_runtime()))

            # check for solution
            solved = current_state.validate()
            if solved:
                # found solution
                print("\nSolved")
                return self.wrap_up_result(current_state, True, self.split_statistics, list(self.initial.bookkeeping.keys()))

            # simplify
            set_literals = []
            valid, potential_problem = current_state.simplify(set_literals, self.is_dependency_graph_active())

            # add difference to order
            for literal in set_literals:
                self.order.append(literal)

            # detect problems
            if not valid:
                # backtrack
                self.handle_problem_clause(current_state, potential_problem)
                continue

            # check again
            solved = current_state.validate()

            if solved:
                # found solution
                print("\nSolved")
                return self.wrap_up_result(current_state, True, self.split_statistics, list(self.initial.bookkeeping.keys()))
            else:
                # split
                future_states, literal = self.split(current_state)
                self.stack[literal] = future_states

    def handle_problem_clause(self, state, literal):
        """
        Triggers backtracke mode and finds a new problem clause to add to knowledge base

        :param state:
        :param literal:
        :return:
        """
        if (not self.is_dependency_graph_active()):
            # not needed in absence of depency graph heuristic
            return

        # up counter
        self.clause_counter += 1

        # get clause
        problem_clause = state.dependency_graph.find_conflict_clause(literal, self.clause_counter)

        # add
        self.problem_clauses.append(problem_clause)

        # trigger a backtrack
        self.backtrack_mode_active = True

    def split(self, current_state: KnowledgeBase) -> Tuple[Dict[bool, KnowledgeBase], int]:
        """
        Generator for a splits given a current knowledge base and its current truth value assignments

        :param current_state:
        :return:
        """

        # init with none
        new_states = {True: None, False: None}

        self.timestep += 1

        # choose a literal
        literal = random.choice(list(current_state.bookkeeping.keys()))
        while literal in current_state.current_set_literals:
            literal = random.choice(list(current_state.bookkeeping.keys()))

        # add literal to order
        self.order.append(literal)

        for truth_assignment in [False, True]:

            new_state = self.data_manager.duplicate_knowledge_base(current_state, self.timestep, use_dependency_graph=self.is_dependency_graph_active())

            # do split
            valid, potential_problem = new_state.set_literal(literal, truth_assignment, split=True, dependency_graph=self.is_dependency_graph_active())

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

        if (not self.is_dependency_graph_active() or not self.backtrack_mode_active):

            # if not in error mode: depth first state expansion
            return self.chronological_backtracking()

        else: # backtrack

            # print("backtrack")

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
                    state = self.data_manager.duplicate_knowledge_base(stack_state, stack_state.timestep, use_dependency_graph=self.is_dependency_graph_active())
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
                raise RestartException(f"\nBacktrack limit of {self.backtrack_limit} exceeded", restart = True, stats=self.split_statistics, elapsed_runtime=self.get_elapsed_runtime())

            return state

    def get_elapsed_runtime(self):
        return timeit.default_timer() - self.start


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

        raise RestartException("Could not find backtrack literal!", restart=True, stats=self.split_statistics, elapsed_runtime=self.get_elapsed_runtime())

    def add_problem_clauses_to_state(self, state):
        """
        Adds list of discovered problem clauses to new state

        :param state:
        :return:
        """
        valid = state.add_clauses(self.data_manager.personal_deepcopy(self.problem_clauses))
        if (not valid):
            raise RestartException("Adding clauses led to invalid addition!", restart=True, stats=self.split_statistics, elapsed_runtime=self.get_elapsed_runtime())

    def chronological_backtracking(self) -> KnowledgeBase:
        # reset infinite loop detection
        self.cyclefree = defaultdict(int)

        # find state values
        # Find the first literal in the order that has a state in the stack
        for last_literal in reversed(self.order):
            if last_literal in self.stack:
                break

        choices = list(self.stack[last_literal].keys())

        truth_assignment = random.choice(choices)

        # find state
        if (self.is_dependency_graph_active()):
            state = self.stack[last_literal][truth_assignment]
            state = self.data_manager.duplicate_knowledge_base(state, state.timestep, use_dependency_graph=self.is_dependency_graph_active())

            # add problem clauses
            self.add_problem_clauses_to_state(state)
        else:
            state = self.stack[last_literal].pop(truth_assignment)
            if (len(self.stack[last_literal]) == 0):
                # backtrack to most recent
                del self.stack[last_literal]
                self.order = self.order[:self.order.index(last_literal)+1]

        return state

    def is_dependency_graph_active(self) -> bool:
        return self.heuristics["DependencyGraph"]
