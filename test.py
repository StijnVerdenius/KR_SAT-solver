from solver.clause import Clause
from solver.knowledge_base import KnowledgeBase
from solver.solver_cdcl_dpll import CDCL_DPLL_Solver
from main import get_settings

def test_solver_tautology():
    clauses = {1: Clause(1, [1, 2, 3, -1])}
    kb = KnowledgeBase(clauses, clause_counter=1)
    s = CDCL_DPLL_Solver(kb)

    assert s.solve_instance()[1] is True


def test_solver_diplomatic_puzzle():
    clauses = {1: Clause(1, [1, -2]), 2: Clause(2, [2, 3]), 3: Clause(3, [-3, -1])}
    kb = KnowledgeBase(clauses, clause_counter=3)
    s = CDCL_DPLL_Solver(kb)

    res, solved = s.solve_instance()

    assert res.current_set_literals == {1:True, 2: True, 3: False}
    assert solved is True

def test_solver_case3():

    clauses = [Clause(1, [1, -2]), Clause(2, [1, -3, 2]), Clause(3, [3, 2, -1]), Clause(4, [-2, -1, 3])]
    clauses = {clause.id: clause for clause in clauses}
    kb = KnowledgeBase(clauses, clause_counter=3)
    s = CDCL_DPLL_Solver(kb)

    res, solved = s.solve_instance()

def test_solver_case4():
    ls = [[1,4], [1,-3,-8], [1,8,12], [2,11], [-7,-3,9], [-7,8,-9], [7,8,-10], [7,10,-12]]
    settings = get_settings(1)
    clauses = [Clause(i, l) for i, l in enumerate(ls)]
    clauses = {clause.id: clause for clause in clauses}
    kb = KnowledgeBase(clauses, clause_counter=len(clauses))
    s = CDCL_DPLL_Solver(kb, split_stats=[], heuristics=settings)

    res, solved, stats = s.solve_instance()
    print(res.current_set_literals, stats)

def test_solver_case5():
    ls = [[-1, -2, -3], [-1, -2], [-2,-3], [-1,-3]]
    clauses = [Clause(i, l) for i, l in enumerate(ls)]
    clauses = {clause.id: clause for clause in clauses}
    kb = KnowledgeBase(clauses, clause_counter=len(clauses))
    s = CDCL_DPLL_Solver(kb)

    res, solved, _ = s.solve_instance()
    print(res.current_set_literals)

test_solver_case4()