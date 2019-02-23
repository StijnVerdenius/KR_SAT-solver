import itertools
from typing import Tuple, List, Generator, Dict
from solver.saver import Saver
from solver.knowledge_base import KnowledgeBase
from solver.clause import Clause
from collections import deque, defaultdict
import random
try:
    import numpy as np
except ImportError:
    raise RuntimeError("Please install numpy")
import timeit

class Solver:

    def __init__(self, knowledge_base : KnowledgeBase):
        self.initial = knowledge_base
        self.saver = Saver("./temp/")
        self.timestep = 0
        self.clause_counter = self.initial.clause_counter

        self.currently_conflict_mode = False
        self.problem_clauses = []
        self.order = ["init"]
        self.stack = {}

    def solve_instance(self) -> Tuple[KnowledgeBase, bool, List]:
        """ main function for solving knowledge base """
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
        self.problem_clauses[state.timestep].add(problem_clause)

        # trigger a backtrack
        self.currently_conflict_mode = True

    def expand_tree_by_split(self, current_state: KnowledgeBase) -> Tuple[Dict[bool, KnowledgeBase], int]:
        """
        Generator for possible splits given a current knowledge base and its current truth value assignments

        :param current_state:
        :return:
        """

        # init with none
        new_states = {True : None, False : None}

        self.timestep += 1

        # choose a literal todo: heuristiek ipv random
        literal = random.choice(current_state.bookkeeping.keys())
        while literal in current_state.current_set_literals:
            literal = random.choice(current_state.bookkeeping.keys())

        # add literal to order
        self.order.append(literal)

        for truth_assignment in [False, True]:

            new_state = self.saver.deepcopy_knowledge_base(current_state, self.timestep)

            # do split
            valid, potential_problem = new_state.set_literal(literal, truth_assignment)

            if not valid:

                self.retrieve_problem_clause(new_state, literal)

                continue

            else:

                # problem free
                new_states[truth_assignment] = new_state

        return new_states

    def get_next_state(self) -> KnowledgeBase:

        # if not in error mode: depth first state expansion
        if (not self.currently_conflict_mode):

            # find state values
            literal = self.order[-1]
            truth_assignment = random.choice([True, False]) # todo: hearistiek ipv random

            # find state
            state = self.stack[literal].pop(truth_assignment)

            if (state is None):
                raise Exception("None-state")
                # todo: dit betekent dat in split een fout gaf voor 1 van de twee states en die het somehow overleeft heeft, wat hieraan te doen?

            # add problem clauses
            self.add_problem_clauses_to_state(state)

            return state

        else: # backtrack


            # reset conflict mode
            self.currently_conflict_mode = False

            # find relevant problem clause
            problem_clause = self.problem_clauses[-1]

            # todo: find earliest literal from problem clause in self.order

            # todo: find corresponding state in stack
            state = None

            self.add_problem_clauses_to_state(state)

            # todo: remove literals that came after from self.order

            # todo: remove literals that came after from self.stack

            return state

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