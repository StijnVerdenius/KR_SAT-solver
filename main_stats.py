import os
from functools import partial

from solver.data_management import DataManager
from solver.stats import show_stats


def add_version_number(item, vn):
    return (*item, vn)


if __name__ == "__main__":  # TODO: remove
    dm = DataManager(os.getcwd() + '/results/')
    sudokus_stats = dm.load_python_obj('experiment-v3')

    # add = partial(add_version_number, vn=3)
    # sudokus_stats = map(add, sudokus_stats)

    sudokus_stats += dm.load_python_obj('experiment-v2')
    sudokus_stats += dm.load_python_obj('experiment-v1')
    # add = partial(add_version_number, vn=2)
    # sudokus_stats2 = map(add, sudokus_stats)

    show_stats(sudokus_stats)