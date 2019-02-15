from code.clause import Clause

class KnowledgeBase:

    def __init__(self, clauses = None, current_truth_values = None, bookeeping = None, counter = 0, literal_set = None):

        # clauses
        if clauses is None:
            self.clauses = []
        else:
            self.clauses = clauses

        # current assignment for literals
        if current_truth_values is None:
            self.current_truth_values = {}
        else:
            self.current_truth_values = current_truth_values

        # bookkeeping references
        if bookeeping is None:
            self.bookkeeping = {}
        else:
            self.bookkeeping = bookeeping

        # counts amount of clauses
        self.clause_counter = counter

        # keeping track of the amount of literals
        if literal_set is None:
            self.literal_set = set()
        else:
            self.literal_set = literal_set


    def validate(self):
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