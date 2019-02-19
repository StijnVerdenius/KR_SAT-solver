from collections import namedtuple
from typing import List
try:
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt
except ImportError as e:
    raise RuntimeError("Please install numpy && Seaborn && matplotlib")

Split = namedtuple('Split', ['literal_cnt', 'clause_cnt'])

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
