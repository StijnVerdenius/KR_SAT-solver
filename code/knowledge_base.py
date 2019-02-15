from code.clause import Clause

class KnowledgeBase:

    def __init__(self, clauses = None, current_truth_values = None, bookeeping = None, counter = 0, literal_set = set()):
        if clauses is None:
            self.clauses = []

        self.current_truth_values = current_truth_values
        self.bookkeeping = bookeeping
        self.clause_counter = counter
        self.literal_set = literal_set
        # self.dependency_graph = {}

    def copy(self):
        return

    def validate(self, assignment):
        pass

    def insert_rules(self, rules):
        """ inserts rules to knowledge base """

        for rule in rules:
            self.clauses.append(Clause(self.clause_counter, rule))
            for literal in rule:
                self.literal_set.add(literal)
                try:
                    self.bookkeeping[literal].append(literal)
                except:
                    self.bookkeeping[literal] = [literal]
            self.clause_counter += 1

    def capture_current_state(self):
        pass

    def simplify(self, state):
        pass