import numpy as np
import math
from itertools import permutations
from pysat.solvers import Glucose3

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

def random_board():
    # Generate a random number as dimension n
    n = np.random.randint(4,16) # Use this once you get past testing algo
    # n = np.random.randint(4,10)
    n = math.floor(math.sqrt(n))**2
    
    #idea for preventing immediately conflicting boards:
    #start with empty board, 0's everywhere
    #whatever percent p of filled squares is
    #pick random board positions
    #fill with random value, except check that the value is legal
    #if not legal, either try antoher value in same cell, or just try another place altogether. idk which is more 'random'
    
    #n x n board filled with 0's
    board_2 = np.zeros((n,n), dtype=int)
    
    #let's go for 25% filled
    f = int(0.25 * n * n)
    
    #we want to fill f number of cells
    while (f > 0):
        f -= 1
        
        #random row and col, therefore a random cell
        row = np.random.randint(0,n)
        col = np.random.randint(0,n)
        #value v we want to insert into cell
        v = np.random.randint(1,n+1)
        board_2[row,col] = v
        
        #counter to prevent infinite loop if a cell is impossible to legally fill for some reason
        #idk if this will ever trigger, as an unfillable cell implies a broken board, but idk 
        #better to be safe than sorry
        count = 0
        
        #if that value fucks up the board, try a new v
        while (check_still_viable(board_2) == False or count > n):
            count += 1
            
            #try v + 1, mod n+1, so only values [0,n] are possible
            v = (v + 1) % (n + 1)
            
            #v=0 makes an empty cell, so skip that value
            if (v==0):
                v = 1
            
            #reattempt value
            board_2[row,col] = v
    
    return board_2

def dpll_sudoku(board, x_idx, y_idx, cells_filled, n):
    # Base cases: either invalid board, or filled properly
    if not check_still_viable(board):
        return False
    elif cells_filled == n**2:
        return True
    else:
        # Fill with a guess if not empty
        if board[x_idx][y_idx] == 0:
            for i in range(1, n+1):
                board[x_idx][y_idx] = i
                if x_idx < n-1:
                    viable = dpll_sudoku(board, x_idx+1, y_idx, cells_filled+1, n)
                else:
                    viable = dpll_sudoku(board, 0, y_idx+1, cells_filled+1, n)
                # Check if viable path -- if so, we have a solution
                if viable:
                    return True
            board[x_idx][y_idx] = 0
        else:
            if x_idx < n-1:
                viable = dpll_sudoku(board, x_idx+1, y_idx, cells_filled+1, n)
            else:
                viable = dpll_sudoku(board, 0, y_idx+1, cells_filled+1, n)
            # Check if viable path -- if so, we have a solution
            if viable:
                return True
    return False

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
    # Every combo of negated duos -- permutations of k literals + k negated, choose k -- but use set to filter repeats
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

def reduction_pythonSAT(board, g):
    # Ensure there will never be an empty setup -- since 0 will not be used anywhere else (all clauses should hav >= 2 digits)
    # we can guarantee that it won't affect the outcome -- you can just always set to true
    g.add_clause([1])
    # Calculate essential constants
    n = len(board)
    root = int(math.sqrt(n))
    k = math.ceil(math.log(n, 2))
    invalid_bin_vals = [to_binary(i, k) for i in range(n+1, 2**k+1)]
    
    # ORDERING STEPS FROM SMALLEST TO LARGEST CLAUSES (for unit propagation)
    
    # Step 1: Encode filled in cells
    for r in range(n):
        for c in range(len(board[r])):
            if board[r][c] != 0:
                bin_val = to_binary(board[r][c], k)
                for bit_idx in range(len(bin_val)):
                    if bin_val[bit_idx] == '1':
                        g.add_clause([int(str(r+1) + str(c+1) + str(bit_idx+1))])
                    else:
                        g.add_clause([-1*int(str(r+1) + str(c+1) + str(bit_idx+1))])
    
    # Step 2: Go through every cell and make sure bit values are definitely not invalid
    for r in range(n):
        for c in range(len(board[r])):
            for val in invalid_bin_vals:
                new_clause = []
                for bit_idx in range(k):
                    factor = 1
                    if val[bit_idx] == '1':
                        factor = -1
                    new_clause.append(factor*int(str(r+1) + str(c+1) + str(bit_idx+1)))
                # Write off string to file
                g.add_clause(new_clause)
    
    # Step 3: Ensure each cell is different from its row, column, and local block neighbors
    # Loop through every cell in the board -- can probably combine this with steps 1 and 3
    # (we don't actually have to know values though -- just use indices) [row and col = n, cell sqrt(n) x sqrt(n)]
    for r in range(n):
        for c in range(len(board[r])):
            for row_idx in range(n):
                if row_idx != r:
                    # Generate block of comparison code for current cell and cell to differentiate
                    new_clauses = gen_compare_block_python_SAT(str(r+1) + str(c+1), str(row_idx+1) + str(c+1), k)
                    # Write block of comparison code to file
                    for clause in new_clauses:
                        g.add_clause(clause)
                    
            for col_idx in range(n):
                if col_idx != c:
                    # Generate block of comparison code for current cell and cell to differentiate
                    new_clauses = gen_compare_block_python_SAT(str(r+1) + str(c+1), str(r+1) + str(col_idx+1), k)
                    # Write block of comparison code to file
                    for clause in new_clauses:
                        g.add_clause(clause)
            
            # Get cell and do generation
            cell_start_r = (r // root)*root
            cell_start_c = (c // root)*root
            for sub_row in range(cell_start_r, cell_start_r + root):
                for sub_col in range(cell_start_c, cell_start_c + root):
                    if sub_row != r and sub_col != c:
                        # Generate block of comparison code for current cell and cell to differentiate
                        new_clauses = gen_compare_block_python_SAT(str(r+1) + str(c+1), str(sub_row+1) + str(sub_col+1), k)
                        # Write block of comparison code to file
                        for clause in new_clauses:
                            g.add_clause(clause)
    return g


if __name__ == '__main__':
    countTrue = 0
    total = 10
    dictionary = {}
    for i in range(total):
        test_pythonSAT = random_board()
        g = Glucose3()
        new_g = reduction_pythonSAT(test_pythonSAT, g)
        
        length = len(test_pythonSAT)
        if length not in dictionary:
            dictionary[length] = 1
        else:
            dictionary[length] += 1
        
        truth = new_g.solve()
        if truth:
            countTrue += 1
            
        print(length, truth)

    print(countTrue, 'boards were true out of', total)
    print(dictionary)


