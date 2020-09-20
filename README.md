# CSCI4114-PSET3

NP-Complete programs are notoriously hard to solve, especially as the problem instances grow in size. However, due to years upon years of research efforts, CNF-SAT solvers have gotten incredibly good, so much so that reducing other NP-Complete problems to CNF-SAT and running them through a SAT solver has become even more efficient than optimzied algorithms specific to the chosen NP-Complete problem. 

This project demonstrates exactly that: the selected problem, Sudoku for dimensions of length n, is an NP-Complete problem. There are two algorithms in this repository to solve it:

1. DPLL-style backtracking algorithm
2. Sudoku-SAT Reduction + Python-SAT's Glucose3 SAT Solver

As we will see from running both algorithms, reducing Sudoku to SAT and then running it through a state-of-the-art SAT Solver is much more efficient than trying to write a Sudoku-specific algorithm (albeit, this implementation could be further optimized).

## Usage
To run this file, first ensure that Python-SAT is installed. You can install it with pip:
```
> pip install python-sat
```
Some test code already exists in the file, though due to the slow nature of the DPLL algorithm, will be quite lengthy to run. It is recommended that you alter the main code before running the code with:
```
> python main.py
```

## DPLL Algorithm
A DPLL algorithm is a brute force backtracking algorithm that eliminates subsets of configurations by discarding paths as soon as a contradiction is found. For Sudoku, that means it attempts to fill in a cell with a value from 1 to n, and if the board is still valid after that guess, tries to fill in more cells. If the board is invalid, the algorithm tries a different guess before moving on.

This particular DPLL algorithm has constraint propagation implemented, which makes it slightly faster than the naive algorithm.

The DPLL algorithm is implemented in `dpll_sudoku()`.

## Reduction to CNF-SAT
The reduction to SAT encodes 3 main rules for Sudoku:

1. Every cell must contain a single value from 1 to n
2. Every cell must be different from other cells in the same row, column, or local block.
3. Given cells (i.e. cells that have been filled in) must keep their given value.

The Sudoku to SAT reduction algorithm is implemented in `reduction_pythonSAT()`.