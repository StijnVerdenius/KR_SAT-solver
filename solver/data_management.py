try:
    import pickle as pickle
except ImportError:
    raise RuntimeError("Please install _pickle & pickle package")

from solver.knowledge_base import KnowledgeBase
from solver.dependency_graph import DependencyGraph
from collections import defaultdict
from typing import Dict, Tuple
from solver.clause import Clause
try:
    import numpy as np
except ImportError:
    raise RuntimeError("Please install numpy")
import math

class DataManager():

    def __init__(self, directory):

        # determines relative disk directory for saving/loading
        self.directory = directory

    def save_python_obj(self, obj, name):
        """ Saves python object to disk in pickle """

        try:
            with open(self.directory + name+".pickle", 'wb') as handle:
                pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)
            print("Saved {}".format(name))
        except Exception as e:
            print(e)
            print("Failed saving {}, continue anyway".format(name))

    def load_python_obj(self, name):
        """ Loads python object from disk if pickle """

        obj = None
        try:
            with (open(self.directory + name+".pickle", "rb")) as openfile:
                obj = pickle.load(openfile)
        except FileNotFoundError:
            raise FileNotFoundError("{} not loaded because file is missing".format(name))
        print("Loaded {}".format(name))
        return obj

    def personal_deepcopy(self, obj):
        """ Deep copies any object faster than builtin """

        return pickle.loads(pickle.dumps(obj, protocol=-1))

    def duplicate_knowledge_base(self, base : KnowledgeBase, step : int, use_dependency_graph=False):
        """ Deep copies a KB """

        clauses_ = self.personal_deepcopy(base.clauses)
        set_literals_ = self.duplicate_dict(base.current_set_literals)
        bookkeeping_ = self.duplicate_default_dict(base.bookkeeping, self.duplicate_set, set)

        # dependency graph stuff
        if (use_dependency_graph):
            initial_ = self.duplicate_default_dict(base.dependency_graph.initial_coocurrence, self.duplicate_set, set)
            graph_ = self.duplicate_default_dict(base.dependency_graph.graph, self.duplicate_set, set)
            dependency_graph_ = DependencyGraph(initial=initial_, graph=graph_, existing_literals=list(set_literals_.keys()))
        else:
            dependency_graph_ = use_dependency_graph

        return KnowledgeBase(clauses=clauses_,
                             current_set_literals= set_literals_,
                             bookkeeping=bookkeeping_,
                             clause_counter= base.clause_counter,
                             literal_counter= base.literal_counter,
                             dependency_graph=dependency_graph_,
                             timestep=step)



    def duplicate_list(self, lst: list) -> list:
        """ shallow copies list """

        return [x for x in lst]

    def duplicate_set(self, st: set) -> set:
        """ shallow copies set """

        return {x for x in st}

    def duplicate_dict(self, dc) -> dict:
        """ shallow copies dictionary """
        return {key : dc[key] for key in dc}

    def duplicate_default_dict(self, dfdc, type_func, typ) -> defaultdict:
        """ shallow copies a defualtdictionary but gives tha chance to also shallow copy its members """

        output = defaultdict(typ)
        for key in dfdc:
            output[key] = type_func(dfdc[key])
        return output

    def dump_only(self, obj):
        return pickle.dumps(obj, protocol=-1)

    def load_only(self, obj):
        return pickle.loads( obj)

    def to_dimacs_str(self, knowledge_base: KnowledgeBase):
        """
        Transfers knowledge base back to dimacs (string)

        :param knowledge_base:
        :return:
        """

        file = []
        literals = list(filter(lambda x: x > 0, knowledge_base.current_set_literals.keys()))
        file.append("p cnf 81 90")
        for literal in literals:

            if (not knowledge_base.current_set_literals[literal]):
                continue

            file.append(f"{literal} 0\n")

        return "".join(file)

    def read_rules_string(self, rules_str: str, id: int) -> Tuple[Dict[int, Clause], int]:
        """
        Read rules from dimacs string into datastructure

        :param rules_str:
        :param id:
        :return:
        """

        # TODO: error on file nt found
        clauses = {}
        for line in rules_str.split("\t"):
            tokens = line.split(' ')
            if tokens[-1] != '0\n':
                continue

            literals = [int(token) for token in tokens[0:-1]]

            clauses[id] = Clause(id, literals)
            id += 1

        return clauses, id

    def read_rules_dimacs(self, rules_path: str, id: int) -> Tuple[Dict[int, Clause], int]:
        """
        reads dimacs rules from file into string, then transfers to datastructure with read_rules_string function

        :param rules_path:
        :param id:
        :return:
        """

        # TODO: error on file nt found
        with open(rules_path) as f:
            stringbuilder = "{}"

            for line in f:
                stringbuilder = stringbuilder.format(line + "\t{}")

        return self.read_rules_string(stringbuilder.replace("\n{}", ""), id)

    def read_text_sudoku(self, puzzle_path: str, puzzle_number: int, id: int) -> Tuple[Dict[int, Clause], bool, int]:
        """
        Reads one-liner sudoku into dimacs string, returns data structure through read_rules_string function

        :param puzzle_path:
        :param puzzle_number:
        :param id:
        :return:
        """

        with open(puzzle_path) as f:
            for i, line in enumerate(f):

                if (i == puzzle_number):

                    # print(line)

                    line = line.replace("\n", "")

                    template = np.zeros((len(line), 1))

                    for j, letter in enumerate(line):

                        if (not letter == "."):

                            try:

                                template[j, 0] = int(letter)

                            except ValueError:

                                continue

                    template = template.reshape((int(math.sqrt(len(line))), int(math.sqrt(len(line)))))

                    # print(template)

                    output = "{}"

                    for y in range(len(template)):

                        for x in range(len(template)):

                            if (not template[y, x] == 0):
                                output = output.format(str(x + 1) + str(y + 1) + str(int(template[y, x])) + " 0\n\t{}")

                    returnvalues = self.read_rules_string(output.replace("\n{}", ""), id)

                    return returnvalues[0], True, returnvalues[1]

        return None, False, id
