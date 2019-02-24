import os
from collections import namedtuple
from typing import List

from solver.data_management import DataManager

try:
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt
    import pandas as pd
except ImportError as e:
    raise RuntimeError("Please install numpy && Seaborn && matplotlib")

Split = namedtuple('Split', ['literal_cnt', 'clause_cnt'])

def show_stats(sudokus_stats):
    literal_cnts = []
    clause_cnts = []
    sudoku_nrs = []
    xs = []
    algorithms = []
    algorithm_names = {2: 'CDCL', 3: 'Look-Ahead'}
    for splits, sudoku_nr, program_version in sudokus_stats:
        x = 0
        for j, split in enumerate(splits):
            literal_cnts.append(split.literal_cnt)
            clause_cnts.append(split.clause_cnt)
            sudoku_nrs.append(sudoku_nr)
            xs.append(x)
            algorithms.append(algorithm_names[program_version])

            x += 1
            # y[i, j] = split.literal_cnt

    d = {'Literals': literal_cnts, 'Clauses':clause_cnts, 'Sudoku': sudoku_nrs, 'Splits': xs, 'algorithm': algorithms}
    df = pd.DataFrame(data=d)
    print(df)

    sns.lineplot(x="Splits", y='Literals', data=df)
    # plt.xlabel("Splits")
    # plt.ylabel("Clauses")
    plt.show()

    sns.lineplot(x="Splits", y='Literals', data=df, hue="Sudoku")
    # plt.xlabel("Splits")
    # plt.ylabel("Clauses")
    plt.show()

    sns.lineplot(x="Splits", y='Clauses', data=df, hue="Sudoku")
    # plt.xlabel("Splits")
    # plt.ylabel("Clauses")
    plt.show()

    sns.lineplot(x="Splits", y='Literals', data=df, hue='algorithm')
    # plt.xlabel("Splits")
    # plt.ylabel("Clauses")
    plt.show()


    # for sudoku in sudokus:
    # sns.set(style="darkgrid")
    # x = np.arange(0, len(splits_statistics))
    # y = [split.clause_cnt for split in splits_statistics]
    # sns.lineplot(x, y)
    # plt.xlabel("Splits")
    # plt.ylabel("Clauses")
    # plt.show()
    #
    # x = np.arange(0, len(splits_statistics))
    # y = [split.literal_cnt for split in splits_statistics]
    # sns.lineplot(x, y)
    # plt.xlabel("Splits")
    # plt.ylabel("Literals")
    # plt.show()



def print_stats(splits_statistics: List[Split]):
    clause_cnt = splits_statistics[0].clause_cnt
    literal_cnt = splits_statistics[0].literal_cnt

    print()
    print(f"{'-' * 10} Statistics {'-' * 10}")
    print(f"Number of splits: {len(splits_statistics)}")

    print(f"Splits:")
    for split_nr, split  in enumerate(splits_statistics):
        clause_cnt = split.clause_cnt
        literal_cnt = split.literal_cnt

        print(f"Split nr: {split_nr}")
        print(f"Clauses: {clause_cnt}")
        print(f"Literals: {literal_cnt}")
        print(f"C / L ratio: {clause_cnt / literal_cnt}")

        break

    sns.set(style="darkgrid")
    x = np.arange(0, len(splits_statistics))
    y = [split.clause_cnt for split in splits_statistics]
    sns.lineplot(x, y)
    plt.xlabel("Splits")
    plt.ylabel("Clauses")
    plt.show()

    x = np.arange(0, len(splits_statistics))
    y = [split.literal_cnt for split in splits_statistics]
    sns.lineplot(x, y)
    plt.xlabel("Splits")
    plt.ylabel("Literals")
    plt.show()

    print(f"{'-' * 10} Statistics {'-' * 10}")


