import numpy as np
import math
import time
from pysat.solvers import Glucose3
from itertools import permutations

#------------------------------------------------------------#
#                  General Helper Functions                  #
#------------------------------------------------------------#

def check_still_viable(board):
    # Get n val and its root
    n = len(board)
    root = int(math.sqrt(n))

    # Check if valid
    for i in range(n):
        row = board[i]
        col = board[ : , i]
        # Check rows
        for r_idx in range(len(row)-1):
            if row[r_idx] != 0 and row[r_idx] in row[r_idx+1:]:
                return False
        # Check cols
        for c_idx in range(len(col)-1):
            if col[c_idx] != 0 and col[c_idx] in col[c_idx+1:]:
                return False
        # Check squares
        if i % root == 0:
            for j in range(0, n, root):
                subsection = board[i:i+root, j:j+root]
                subsection_row = np.array([])
                # Combine all into a single row
                for item in subsection:
                    subsection_row = np.concatenate([subsection_row, item])
                # Check if valid
                for s_idx in range(len(subsection_row)-1):
                    if subsection_row[s_idx] != 0 and subsection_row[s_idx] in subsection_row[s_idx+1:]:
                        return False

    return True

def random_board(n):
    """
    Idea for preventing immediately conflicting boards:
    - Start with empty board, 0's everywhere
    - Whatever percent p of filled squares is
    - Pick random board position
    - Fill with random value, except check that the value is legal
    - If not legal, either try antoher value in same cell
    """
    # Generate n x n board filled with 0's and calculate num cells to fill f
    board_2 = np.zeros((n,n), dtype=int)
    f = int(0.3 * n * n)
    
    # Fill f number of cells
    while (f > 0):
        f -= 1

        # Generate random cell position and value
        row = np.random.randint(0,n)
        col = np.random.randint(0,n)
        v = np.random.randint(1,n+1)
        board_2[row,col] = v
        
        # Counter to prevent infinite loop if a cell is impossible to legally fill for some reason
        count = 0
        
        # If added value messes up the board, try a new v
        while (check_still_viable(board_2) == False or count > n):
            count += 1
            
            # Ensure only values [0,n] are possible (but skip 0 since that represents an empty cell)
            v = (v + 1) % (n + 1)
            if (v==0):
                v = 1
            
            # Reattempt value
            board_2[row,col] = v
    
    return board_2

#------------------------------------------------------------#
#       DPLL-Style Backtracking Algo Helper Functions        #
#------------------------------------------------------------#

def constraint_propagation(board):
    # Dictionary holds each cell and the values it's allowed to be
    dictionary = {}
    filled = []
    n = len(board)
    root = int(math.sqrt(n))
    
    # Start off each cell with being allowed to be all values
    for r in range(n):
        for c in range(len(board[r])):
            if board[r][c] != 0:
                dictionary[(r,c)] = [board[r][c]]
                filled.append((r,c))
            else:
                dictionary[(r,c)] = [i for i in range(1,len(board)+1)]
    
    # Part 1: If we know a square has to be one value, eliminate that value from the squares around it
    for coordinate in filled:
        to_remove = dictionary[coordinate][0]
        for i in range(len(board)):
            check_row = dictionary[(coordinate[0], i)]
            check_col = dictionary[(i, coordinate[1])]
            # Go through all in same row and delete the value
            if to_remove in check_row and (coordinate[0], i) != coordinate:
                check_row.remove(to_remove)
            # Go through all in same col and delete the value
            if to_remove in check_col and (i, coordinate[1]) != coordinate:
                check_col.remove(to_remove)
        # Go through all in same neighbor block and delete the value
        cell_start_r = (coordinate[0] // root)*root
        cell_start_c = (coordinate[1] // root)*root
        for sub_row in range(cell_start_r, cell_start_r + root):
            for sub_col in range(cell_start_c, cell_start_c + root):
                check_cell = dictionary[(sub_row, sub_col)]
                if sub_row != coordinate[0] or sub_col != coordinate[1]:
                    if to_remove in check_cell:
                        check_cell.remove(to_remove)
    
    # Part 2: Check through the rest. If there is a value that doesn't belong to others, must be current
    for coordinate in dictionary:
        if coordinate not in filled:
            # If not already filled, look at all neighbors and see if neighbors have same value
            for val in dictionary[coordinate]:
                assign = True
                # Rows and cols
                for i in range(len(board)):
                    row = dictionary[(coordinate[0], i)]
                    col = dictionary[(i, coordinate[1])]
                    # Go through all in same row check if there
                    if to_remove in row and (coordinate[0], i) != coordinate:
                        assign = False
                        break
                    # Go through all in same col and check if there
                    if to_remove in col and (i, coordinate[1]) != coordinate:
                        assign = False
                        break
                        
                # Sub cells
                # Go through all in same neighbor block and check if there
                cell_start_r = (coordinate[0] // root)*root
                cell_start_c = (coordinate[1] // root)*root
                for sub_row in range(cell_start_r, cell_start_r + root):
                    for sub_col in range(cell_start_c, cell_start_c + root):
                        check_cell = dictionary[(sub_row, sub_col)]
                        if sub_row != coordinate[0] or sub_col != coordinate[1]:
                            if to_remove in check_cell:
                                assign = False
                                break
                
                if assign:
                    dictionary[coordinate] = [val]
                    break
    
    return dictionary

#------------------------------------------------------------#
#               DPLL-Style Backtracking Algo                 #
#------------------------------------------------------------#
"""
Function dpll_sudoku()
@param board: 2D numpy array with integers from 0-n (0 representing empty cells)
@param cells_filled: int representing number of cells filled thus far
@param n: dimension of board
@param ordered: list of tuples indicating possible values for each cell
@return: boolean, whether the board is satisfiable or not
"""
def dpll_sudoku(board, cells_filled, n, ordered):
    # Base cases: either invalid board, or filled properly
    if not check_still_viable(board):
        return False
    elif cells_filled == n**2:
        return True
    elif len(ordered) == 0:
        return False
    else:
        # Fill with a guess if not empty
        # ordered of form: [((0, 1), [5]), ((0, 2), [8]), ((0, 3), [2,3,4])]
        cell_info = ordered[0]
        x_idx = cell_info[0][0]
        y_idx = cell_info[0][1]
        if board[x_idx][y_idx] == 0:
            # Get dictionary of possible values
            for item in cell_info[1]:
                board[x_idx][y_idx] = item
                # Check if viable path -- if so, we have a solution
                if dpll_sudoku(board, cells_filled+1, n, ordered[1:]):
                    return True
            # Reset value if check doesn't work and we backtrack
            board[x_idx][y_idx] = 0
        else:
            # Use given value and check if viable path -- if so, we have a solution
            if dpll_sudoku(board, cells_filled+1, n, ordered[1:]):
                return True
    return False

#------------------------------------------------------------#
#       Sudoku to SAT Reduction Algo Helper Functions        #
#------------------------------------------------------------#
# This func. converts a number to a binary string representation (0b0000 = 1)
def to_binary(n, k):
    n = n-1
    if n == 0:
        return '0'*k
    string = ''
    while n != 0:
        string = str(n%2) + string
        n = n // 2
    # Fill in remaining zeros
    while len(string) < k:
        string = '0' + string
    return string

# This function generates a comparison block of SAT
def gen_compare_block_python_SAT(lit1, lit2, k):
    # Every combo of negated bit pairs
    # Permutations of k literals + k negated, choose k -- but use set to filter repeats
    # Generate a string of 1's and zeros to indicate which should be negated (0's are negated)
    new_clauses = []
    all_combos = permutations('0'*k + '1'*k, k)
    bit_strs = set([''.join(i) for i in all_combos])
    
    # For each bit_str, check if 1 or 0 -- if 0, negate clause
    for bit_str in bit_strs:
        sub_clause = []
        for bit in range(k):
            factor = 1
            if bit_str[bit] == '0':
                factor = -1
            sub_clause.append(factor*int(lit1 + str(bit+1)))
            sub_clause.append(factor*int(lit2 + str(bit+1)))
        new_clauses.append(sub_clause)
    return new_clauses

#------------------------------------------------------------#
#               Sudoku to SAT Reduction Algo                 #
#------------------------------------------------------------#
"""
Function reduction_pythonSAT()
@param board: 2D numpy array with integers from 0-n (0 representing empty cells)
@param g: Glucose3 SAT solver instance to which we will add clauses
@return: Glucose3 SAT solver instances g
"""
def reduction_pythonSAT(board, g):
    # Ensure there will never be an empty setup -- since 1 will not be used anywhere else 
    # (all clauses should hav >= 2 digits)
    # We can guarantee that it won't affect the outcome -- you can just always set to true
    g.add_clause([1])

    # Calculate essential constants
    n = len(board)
    root = int(math.sqrt(n))
    k = math.ceil(math.log(n, 2))
    invalid_bin_vals = [to_binary(i, k) for i in range(n+1, 2**k+1)]
    
    # ORDERING STEPS FROM SMALLEST TO LARGEST CLAUSES (for unit propagation)
    # Note: these steps are out of order because they are numbered according to proof in the pset
    
    # Step 3: Encode filled in cells
    for r in range(n):
        for c in range(len(board[r])):
            if board[r][c] != 0:
                bin_val = to_binary(board[r][c], k)
                for bit_idx in range(len(bin_val)):
                    if bin_val[bit_idx] == '1':
                        g.add_clause([int(str(r+1) + str(c+1) + str(bit_idx+1))])
                    else:
                        g.add_clause([-1*int(str(r+1) + str(c+1) + str(bit_idx+1))])
    
    # Step 1: Go through every cell and make sure bit values are definitely not invalid
    for r in range(n):
        for c in range(len(board[r])):
            for val in invalid_bin_vals:
                new_clause = []
                for bit_idx in range(k):
                    factor = 1
                    if val[bit_idx] == '1':
                        factor = -1
                    new_clause.append(factor*int(str(r+1) + str(c+1) + str(bit_idx+1)))
                g.add_clause(new_clause)
    
    # Step 2: Ensure each cell is different from its row, column, and local block neighbors
    for r in range(n):
        for c in range(len(board[r])):
            # Go through row
            for row_idx in range(n):
                if row_idx != r:
                    # Generate block of comparison code for current cell and cell to differentiate
                    # Adding one to all values because Python-SAT only deals with non-zero values
                    new_clauses = gen_compare_block_python_SAT(str(r+1) + str(c+1), str(row_idx+1) + str(c+1), k)
                    # Add block to g
                    for clause in new_clauses:
                        g.add_clause(clause)

            # Go through column
            for col_idx in range(n):
                if col_idx != c:
                    # Generate block of comparison code for current cell and cell to differentiate
                    new_clauses = gen_compare_block_python_SAT(str(r+1) + str(c+1), str(r+1) + str(col_idx+1), k)
                    # Add block to g
                    for clause in new_clauses:
                        g.add_clause(clause)
            
            # Get local block and do generation
            cell_start_r = (r // root)*root
            cell_start_c = (c // root)*root
            for sub_row in range(cell_start_r, cell_start_r + root):
                for sub_col in range(cell_start_c, cell_start_c + root):
                    if sub_row != r and sub_col != c:
                        # Generate block of comparison code for current cell and cell to differentiate
                        new_clauses = gen_compare_block_python_SAT(str(r+1) + str(c+1), str(sub_row+1) + str(sub_col+1), k)
                        # Add block to g
                        for clause in new_clauses:
                            g.add_clause(clause)
    return g

#------------------------------------------------------------#
#                       Testing Code                         #
#------------------------------------------------------------#
if __name__ == '__main__':
    # Only do up to 16x16, as DPLL algorithm can barely handle 9 already
    total = 100
    sizes = [4,9,16]

    # For each size, indicate
    for size in sizes:
        print('Working on size:', size)
        for i in range(total):
            print('Iteration', i)
            board = random_board(size)

            # Time DPLL solution
            start = time.time()
            dictionary = constraint_propagation(board)
            ordered = sorted(dictionary.items(), key = lambda kv:(len(kv[1]), kv[0])) # Sorts by most constrained
            dpll_sudoku(board, 0, len(board), ordered)
            end = time.time()

            # Time is written in seconds
            file_write = open('dpll' + str(size) + '.csv', 'a')
            file_write.write(str(size) + ',' + str(i) + ',' + str(end-start) + '\n')
            file_write.close()

            # Time reduction solution
            start = time.time()
            new_g = reduction_pythonSAT(test_pythonSAT, g)
            truth = new_g.solve()
            end = time.time()

            # Time is written in seconds
            file_write_2 = open('sat_red' + str(size) + '.csv', 'a')
            file_write_2.write(str(size) + ',' + str(i) + ',' + str(end-start) + '\n')
            file_write_2.close()
            
        print('Done with size', size)


