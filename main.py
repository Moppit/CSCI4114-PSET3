import numpy as np
import math

def check_valid_board(board):
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

if __name__ == '__main__':
    # TODO: this algo mostly produces no instances I think
    # solvable = np.array([1 0 ])
    count = 0
    total = 1000
    for i in range(total):
        test = random_board()
        if(check_valid_board(test)):
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


