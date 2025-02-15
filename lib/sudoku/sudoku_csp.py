import time

from lib.backtracking import backtracking_search, forward_checking, mrv
from lib.constraint_propagation import AC3, implementAC3
from lib.csp import CSP

import itertools
import re
import matplotlib.pyplot as plt
import numpy as np


def flatten(seqs):
    return sum(seqs, [])


def different_values_constraint(A, a, B, b):
    """A constraint saying two neighboring variables must differ in value."""
    return a != b


_R3 = list(range(3))
_CELL = itertools.count().__next__
_BGRID = [[[[_CELL() for x in _R3] for y in _R3] for bx in _R3] for by in _R3]
_BOXES = flatten([list(map(flatten, brow)) for brow in _BGRID])
_ROWS = flatten([list(map(flatten, zip(*brow))) for brow in _BGRID])
_COLS = list(zip(*_ROWS))

_NEIGHBORS = {v: set() for v in flatten(_ROWS)}
for unit in map(set, _BOXES + _ROWS + _COLS):
    for v in unit:
        _NEIGHBORS[v].update(unit - {v})


# ______________________________________________________________________________
# Sudoku
class Sudoku(CSP):
    """A Sudoku problem.
    The box grid is a 3x3 array of boxes, each a 3x3 array of cells.
    Each cell holds a digit in 1..9. In each box, all digits are
    different; the same for each row and column as a 9x9 grid.

    """  # noqa

    R3 = _R3
    Cell = _CELL
    bgrid = _BGRID
    boxes = _BOXES
    rows = _ROWS
    cols = _COLS
    neighbors = _NEIGHBORS

    def __init__(self, grid):
        """Build a Sudoku problem from a string representing the grid:
        the digits 1-9 denote a filled cell, '.' or '0' an empty one;
        other characters are ignored."""
        squares = iter(re.findall(r'\d|\.', grid))
        domains = {var: [ch] if ch in '123456789' else '123456789'
                   for var, ch in zip(flatten(self.rows), squares)}
        for _ in squares:
            raise ValueError("Not a Sudoku grid", grid)  # Too many squares

        # Pruned B=b pairs due to a given A=a assignment.
        # Used to restore domains if an assignment gets backtracked.
        # {A:[(B, b1), (B, b2), (C, c3)], B: [(C, c1)], ...}
        self.pruned = {var: [] for var in domains.keys()}

        CSP.__init__(self, None, domains, self.neighbors, different_values_constraint)

    def display(self, assignment):
        n = 9
        fig_size = 7
        fig = plt.figure(figsize=(fig_size, fig_size))
        ax = fig.add_subplot(111)
        board = np.array([0.5 * int((i + j) % 2) for j in range(n) for i in range(n)]).reshape((n, n))
        a = plt.imshow(board, cmap='Pastel1', interpolation='nearest')

        ax.set_xticks(np.arange(-0.5, 7.5, 3))
        ax.set_yticks(np.arange(-0.5, 7.5, 3))
        plt.grid(color='black')

        ax.tick_params(axis=u'both', which=u'both', length=0)

        for i in assignment:
            plt.text(3 * int((i % 27) / 9) + (i % 9) % 3, 3 * int(i / 27) + int((i % 9) / 3), assignment[i],
                     ha="center", va="center", fontsize=15)
        a.axes.get_xaxis().set_ticklabels([])
        a.axes.get_yaxis().set_ticklabels([])
        plt.show()

if __name__== "__main__":
    nb = 100
    while nb < 1 or nb > 95:
        nb = int(input('Choose the number of the line you want to test'))
    with open("top95.txt") as fp:
        if nb == 1:
            statement = fp.readline()
            print(statement)
        for i, line in enumerate(fp):
            if nb == i + 2:
                statement = fp.readline()
                print(statement)
                break

    # easy1 = '...28.94.1.4...7......156.....8..57.4.......8.68..9.....196......5...8.3.43.28...'
    harder1 = statement
    e = Sudoku(harder1)
    e.display(e.infer_assignment())
    AC3(e);
    start_time = time.time()
    backtracking_search(e, select_unassigned_variable=mrv, inference=forward_checking) is not None
    end_time = time.time()
    print(end_time - start_time)
    e.display(e.infer_assignment())

    start_time = time.time()
    h = Sudoku(harder1)
    h.display(h.infer_assignment())
    backtracking_search(h, select_unassigned_variable=mrv, inference=forward_checking) is not None
    end_time = time.time()
    print(end_time - start_time)
    h.display(h.infer_assignment())