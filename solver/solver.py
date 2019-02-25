from typing import Tuple, List, Generator
from solver.data_management import DataManager
from solver.knowledge_base import KnowledgeBase

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
        self.data_manager = DataManager("./temp/")

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
