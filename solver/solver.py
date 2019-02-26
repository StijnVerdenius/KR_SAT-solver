from solver.data_management import DataManager
from solver.knowledge_base import KnowledgeBase
from typing import Tuple, List
import random

try:
    import numpy as np
except ImportError:
    raise RuntimeError("Please install numpy")
import timeit

class Solver:

    """ Parent calss for common functions among solvers """

    def __init__(self, knowledge_base: KnowledgeBase, problem_id=None):

        # initializing counter
        self.start = 0

        # initial knowledge base
        self.initial = knowledge_base

        # helper for data management
        self.data_manager = DataManager("/temp/")

        # problem id
        self.problem_id = problem_id

    def split(self, current_state: KnowledgeBase):
        raise NotImplementedError("Method needs to be overrided by child-class")

    def solve_instance(self)-> Tuple[KnowledgeBase, bool, List]:
        raise NotImplementedError("Method needs to be overrided by child-class")

    def get_elapsed_runtime(self):
        return timeit.default_timer() - self.start

    def inform_user(self, state: KnowledgeBase, count, start):
        """ Log to user if it takes long """

        # inform user of progress
        if count % 25 == 0:
            runtime = timeit.default_timer() - start
            count = 1
            print(f"\rLength solution: {len(state.current_set_literals)} out of"
                  f" {state.literal_counter}, runtime: {runtime}, number of clauses: "
                  f"{len(state.clauses)}", end='')

        return count

    def wrap_up_result(self, base: KnowledgeBase, solved: bool, stats: List , all_literals: List[int]) -> Tuple[KnowledgeBase, bool, List]:
        """
        Makes sure that literals that are not set yet because their value is irrelevant are set at random.

        :param base:
        :param solved:
        :param stats:
        :param all_literals:
        :return:
        """

        for literal in all_literals:
            if (not literal in base.current_set_literals):
                try:
                    rand_assign = random.choice([True, False])
                    base.set_literal(literal, rand_assign)
                except Exception:
                    pass # ignore

        return base, solved, stats
