import itertools
from typing import Tuple, List, Generator, Dict
from solver.saver import Saver
from solver.knowledge_base import KnowledgeBase
from solver.clause import Clause
from collections import deque, defaultdict
try:
    import numpy as np
except ImportError:
    raise RuntimeError("Please install numpy")
import timeit

TEMPKEY= "TEMPKEY"

class Solver:

    def __init__(self, knowledge_base : KnowledgeBase):
        self.initial = knowledge_base
        self.saver = Saver("./temp/")
        self.problem_clauses = defaultdict(set)
        self.timestep = 0
        self.clause_counter = self.initial.clause_counter

        self.state_dict: Dict[int: KnowledgeBase] = {}
        self.currently_conflict_mode = False
        self.order = []
        self.stack = iter([self.saver.deepcopy_knowledge_base(self.initial, 0)])
        self.last_conflict_literals : Clause = None

    def solve_instance(self) -> Tuple[KnowledgeBase, bool, List]:
        """ main function for solving knowledge base """
        split_statistics = []
        start = timeit.default_timer()
        
        # Check tautology (part of simplify, but only done once)
        self.initial.simplify_tautology()

        solved = False
        count = 0

        while (not solved):
            count += 1
            # get next entry from stack
            try:
                current_state : KnowledgeBase = self.get_next_state()

                split_statistics.append(current_state.split_statistics())

                # inform user of progress
                if count % 25 == 0:
                    runtime = timeit.default_timer() - start
                    count = 1
                    print(f"\rLength solution: {len(current_state.current_set_literals)} out of"
                          f" {current_state.literal_counter}, runtime: {runtime}, number of clauses: "
                          f"{len(current_state.clauses)}", end='')
            except StopIteration:
                return current_state, False, split_statistics


            self.state_dict[TEMPKEY] = self.saver.deepcopy_knowledge_base(current_state, self.timestep)

            # check for solution
            solved, _ = current_state.validate()
            if solved:
                # found solution
                print("\nSolved")
                return current_state, True, split_statistics

            # simplify
            valid, potential_problem = current_state.simplify()
            before = self.state_dict[TEMPKEY].current_set_literals.keys()
            after = current_state.current_set_literals.keys()
            difference = [literal for literal in after if literal not in before]
            for literal in difference:
                self.order.append(literal)
                self.state_dict[literal] = self.state_dict[TEMPKEY]
            if not valid:
                self.clause_counter += 1
                problem_clause = current_state.dependency_graph.find_conflict_clause(potential_problem, self.clause_counter)
                self.problem_clauses[current_state.timestep].add(problem_clause)
                self.last_conflict_literals = problem_clause
                self.currently_conflict_mode = True
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
                self.stack = itertools.chain(future_states, self.stack)

    def possible_splits(self, current_state: KnowledgeBase) -> Generator[KnowledgeBase, None, None]:
        """
        Generator for possible splits given a current knowledge base and its current truth value assignments

        :param current_state:
        :return:
        """

        self.timestep += 1

        local_timestep = self.timestep

        for literal in current_state.bookkeeping.keys():

            if literal in current_state.current_set_literals:
                continue

            for choice in [False, True]:

                new_state = self.saver.deepcopy_knowledge_base(current_state, local_timestep)

                self.state_dict[literal] = self.saver.deepcopy_knowledge_base(new_state, local_timestep)

                # do split
                valid, potential_problem = new_state.set_literal(literal, choice)

                self.order.append(literal)

                if not valid:

                    self.clause_counter += 1

                    # Reached non-valid state, thus leaf-node
                    problem_clause = new_state.dependency_graph.find_conflict_clause(potential_problem,
                                                                                self.clause_counter)
                    self.problem_clauses[new_state.timestep].add(problem_clause)

                    self.order = self.order[:-1]
                    del self.state_dict[literal]

                    self.last_conflict_literals = problem_clause
                    self.currently_conflict_mode = True

                    continue

                else:

                    # self.state_dict[]

                    yield new_state

    def get_next_state(self) -> KnowledgeBase:
        state = None
        if (not self.currently_conflict_mode):
            state = next(self.stack)
            while (state is None):
                state = next(self.stack)
        else:
            self.currently_conflict_mode = False
            last_literals = [abs(lit) for lit in self.last_conflict_literals.literals]
            indices = [self.order.index(lit) for lit in last_literals]
            earliest = last_literals[int(np.argmin(indices))]
            state: KnowledgeBase = self.state_dict[earliest]

            valid, _ = state.set_literal(earliest, earliest in self.last_conflict_literals.literals)

            cutoff = self.order.index(earliest)
            deletables = self.order[cutoff:]
            self.order = self.order[:cutoff]
            for deletable in deletables:
                del self.state_dict[deletable]

        valid = True
        for key in self.problem_clauses:

           # if (key >= state.timestep):
           valid = state.add_clauses(self.problem_clauses[key])

           if (not valid): break

        if (not valid):
           raise Exception("adding clauses led to invalid addition")

        return state




 # # find state
 #            self.currently_conflict_mode = False
 #            indices = [self.order.index(lit) for lit in self.last_conflict_literals]
 #            earliest = self.last_conflict_literals[int(np.argmin(indices))]
 #            timestep = self.descisions[earliest] -1
 #            state: KnowledgeBase = self.state_dict[timestep]
 #
 #
 #
 #            # switch value
 #            valid, _ = state.set_literal(earliest, not self.state_dict[timestep + 1].current_set_literals[earliest])
 #            if (not valid):
 #                raise Exception(f"Both true and false for literal {earliest} give an inconsistency")
 #
 #            # delete whats needed
 #            ind = self.order.index(earliest)+1
 #            deletables = self.order[ind:]
 #            self.order = self.order[:ind]
 #            for deletable in deletables:
 #                del self.descisions[deletable]