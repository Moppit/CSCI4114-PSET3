import numpy as np
import math
import os
from itertools import permutations

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
    n = np.random.randint(4,30) # Use this once you get past testing algo
    # n = np.random.randint(4,10)
    n = math.floor(math.sqrt(n))**2

    # Generate board of n by n size with values up to n
    board = np.random.randint(1, n, size=(n, n))

    # Increase the number of null items (zeroes) to increase chance of solvability
    # The minimum number of spaces that have to be filled is about 23-25% of the spaces
    # So to ensure that we will have a board of a decent chance of solvability,
    # we will aim for about 70% to be converted to zeroes (since some will already be zero)
    for i in range(len(board)):
        for j in range(len(board[i])):
            r = np.random.rand()
            if r < .8:
                board[i][j] = 0

    return board

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
def gen_compare_block(lit1, lit2, k):
    # Every combo of negated duos -- permutations of k literals + k negated, choose k -- but use set to filter repeats
    # Generate a string of 1's and zeros to indicate which should be negated (0's are negated)
    block = ''
    all_combos = permutations('0'*k + '1'*k, k)
    bit_strs = set([''.join(i) for i in all_combos])
    
    # For each bit_str, check if 1 or 0 -- if 0, negate clause
    for bit_str in bit_strs:
        for bit in range(k):
            if bit_str[bit] == '0':
                block += '~' + lit1 + str(bit) + ' ~' + lit2 + str(bit) + ' '
            else:
                block += lit1 + str(bit) + ' ' + lit2 + str(bit) + ' '
        block += '\n'
    return block

# This func. takes a sudoku board and writes config to file
def reduction(board):
    # Open input file
    file_to_write = open('test.in', 'w')
    # Ensure there will never be an empty setup -- since x will not be used anywhere else
    # we can guarantee that it won't affect the outcome -- you can just always set to true
    file_to_write.write('x\n')
    # Calculate essential constants
    n = len(board)
    root = int(math.sqrt(n))
    k = math.ceil(math.log(n, 2))
    invalid_bin_vals = [to_binary(i, k) for i in range(n+1, 2**k+1)]
    
    for r in range(n):
        for c in range(len(board[r])):
            
            # Step 1: Go through every cell and make sure bit values are definitely not invalid
            for val in invalid_bin_vals:
                str_to_write = ''
                for bit_idx in range(k):
                    if val[bit_idx] == '1':
                        str_to_write += '~'
                    str_to_write += str(r) + str(c) + str(bit_idx) + ' '
                str_to_write += '\n'
                # Write off string to file
                file_to_write.write(str_to_write)
            
            # Step 2: Ensure each cell is different from its row, column, and local block neighbors
            # Loop through every cell in the board -- can probably combine this with steps 1 and 3
            # (we don't actually have to know values though -- just use indices) [row and col = n, cell sqrt(n) x sqrt(n)]
            for row_idx in range(n):
                if row_idx != r:
                    # Generate block of comparison code for current cell and cell to differentiate
                    block = gen_compare_block(str(r) + str(c), str(row_idx) + str(c), k)
                    # Write block of comparison code to file
                    file_to_write.write(block)
                    
            for col_idx in range(n):
                if col_idx != c:
                    # Generate block of comparison code for current cell and cell to differentiate
                    block = gen_compare_block(str(r) + str(c), str(r) + str(col_idx), k)
                    # Write block of comparison code to file
                    file_to_write.write(block)
            
            # Get cell and do generation
            cell_start_r = (r // root)*root
            cell_start_c = (c // root)*root
            for sub_row in range(cell_start_r, cell_start_r + root):
                for sub_col in range(cell_start_c, cell_start_c + root):
                    if sub_row != r and sub_col != c:
                        # Generate block of comparison code for current cell and cell to differentiate
                        block = gen_compare_block(str(r) + str(c), str(sub_row) + str(sub_col), k)
                        # Write block of comparison code to file
                        file_to_write.write(block)
    
            # Step 3: Encode filled in cells
            if board[r][c] != 0:
                bin_val = to_binary(board[r][c], k)
                for bit_idx in range(len(bin_val)):
                    if bin_val[bit_idx] == '1':
                        file_to_write.write(str(r) + str(c) + str(bit_idx) + '\n')
                    else:
                        file_to_write.write('~' + str(r) + str(c) + str(bit_idx) + '\n')
    
    file_to_write.close()

# This function runs that file config -- that way we can separate terminal testing
def run_simple_sat():
    stream = os.popen('sat.py --input test.in')
    output = stream.read()
    print('output:', output)


if __name__ == '__main__':
    # TODO: this algo mostly produces no instances I think
    # solvable = np.array([1 0 ])
    count = 0
    total = 1000
    for i in range(total):
        test = random_board()
        if(check_still_viable(test)):
            print(len(test), '', end='')
            if len(test) > 9:
                print('!!! Greater than 9!')
            count += 1
    print()
    print('Got', count, 'solvable boards out of', total)

    """
    Basically the analysis states that the number of boards out of 100 that typically
    work is about 11-12% on average, with nearly all of them being 4x4 and a few being 9x9
    """


