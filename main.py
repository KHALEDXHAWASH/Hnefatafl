class Board:
    def __init__(self):
        self.size = 11
        self.grid = [
            ['C', '.', '.', 'A', 'A', 'A', 'A', 'A', '.', '.', 'C'],
            ['.', '.', '.', '.', '.', 'A', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['A', '.', '.', '.', '.', 'D', '.', '.', '.', '.', 'A'],
            ['A', '.', '.', '.', 'D', 'D', 'D', '.', '.', '.', 'A'],
            ['A', 'A', '.', 'D', 'D', 'K', 'D', 'D', '.', 'A', 'A'],
            ['A', '.', '.', '.', 'D', 'D', 'D', '.', '.', '.', 'A'],
            ['A', '.', '.', '.', '.', 'D', '.', '.', '.', '.', 'A'],
            ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', 'A', '.', '.', '.', '.', '.'],
            ['C', '.', '.', 'A', 'A', 'A', 'A', 'A', '.', '.', 'C']
        ]
    def print_board(self):
        for row in self.grid:
            print(' '.join(row))

    def isvalidmove(self, currentrow, currentcol, newrow, newcol):
        step = 1

        if self.grid[currentrow][currentcol] == '.' or self.grid[currentrow][currentcol] == 'C':
            return False

        if newrow < 0 or newcol < 0 or newrow >= self.size or newcol >= self.size:
            return False

        if self.grid[newrow][newcol] != '.':
            return False

        piece = self.grid[currentrow][currentcol]
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        surrounded = True

        for dr, dc in directions:

            r = currentrow + dr
            c = currentcol + dc

            if 0 <= r < self.size and 0 <= c < self.size:
                if self.grid[r][c] != piece or "K":
                    surrounded = False
                    break
            else:
                surrounded = False
                break

        if surrounded:
            return False

        if newrow == currentrow:
            if newcol < currentcol:
                step = -1
            for i in range(currentcol + step, newcol, step):
                if self.grid[newrow][i] != '.':
                    return False
            return True

        if newcol == currentcol:
            if newrow < currentrow:
                step = -1
            for i in range(currentrow + step, newrow, step):
                if self.grid[i][newcol] != '.':
                    return False
            return True

    def move(self, currentrow, currentcol, newrow, newcol):
        isvalid = self.isvalidmove(currentrow, currentcol, newrow, newcol)
        if isvalid:
            self.grid[newrow][newcol] = self.grid[currentrow][currentcol]
            self.grid[currentrow][currentcol] ='.'
        else:
            print('invalid move')


b = Board()
print("                              ")
b.move(5, 6, 2, 3)
b.print_board()
