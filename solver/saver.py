try:
    import _pickle as pickle
except ImportError:
    raise RuntimeError("Please install _pickle")

from solver.knowledge_base import KnowledgeBase

class Saver():

    def __init__(self, directory):
        self.directory = directory

    def save_python_obj(self, obj, name):
        try:
            with open(self.directory + name+".pickle", 'wb') as handle:
                pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)
            print("Saved {}".format(name))
        except:
            print("Failed saving {}, continue anyway".format(name))

    def load_python_obj(self, name):
        obj = None
        try:
            with (open(self.directory + name+".pickle", "rb")) as openfile:
                obj = pickle.load(openfile)
        except FileNotFoundError:
            raise FileNotFoundError("{} not loaded because file is missing".format(name))
        print("Loaded {}".format(name))
        return obj

    def personal_deepcopy(self, obj):
        return pickle.loads(pickle.dumps(obj, protocol=-1))

    def deepcopy_knowledge_base(self, base : KnowledgeBase):

        clauses_ = self.personal_deepcopy(base.clauses)
        set_literals_ = {key: base.current_set_literals[key] for key in base.current_set_literals}
        bookkeeping_ = self.personal_deepcopy(base.bookkeeping)

        return KnowledgeBase(clauses=clauses_, current_set_literals= set_literals_, bookkeeping=bookkeeping_, clause_counter= base.clause_counter, literal_counter= base.literal_counter)

