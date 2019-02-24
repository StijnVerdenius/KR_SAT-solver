try:
    import pickle as pickle
except ImportError:
    raise RuntimeError("Please install _pickle")

from solver.knowledge_base import KnowledgeBase
from solver.dependency_graph import DependencyGraph
from collections import deque, defaultdict


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

        # todo: copy only the heuristics you use


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


    # def duplicate_knowledge_base(self, base : KnowledgeBase, step : int):
    #
    #     clauses_ = self.personal_deepcopy(base.clauses)
    #     set_literals_ = self.personal_deepcopy(base.current_set_literals)
    #     bookkeeping_ = self.personal_deepcopy(base.bookkeeping)
    #
    #     # dependency graph stuff
    #     initial_ = self.personal_deepcopy(base.dependency_graph.initial_coocurrence)
    #     graph_ = self.personal_deepcopy(base.dependency_graph.graph)
    #     dependency_graph_ = DependencyGraph(initial=initial_, graph=graph_, existing_literals=list(set_literals_.keys()))
    #
    #     return KnowledgeBase(clauses=clauses_,
    #                          current_set_literals= set_literals_,
    #                          bookkeeping=bookkeeping_,
    #                          clause_counter= base.clause_counter,
    #                          literal_counter= base.literal_counter,
    #                          dependency_graph=dependency_graph_,
    #                          timestep=step)    ##### todo; don't throw away!!!
    #
    #     # todo: copy only the heuristics you use
