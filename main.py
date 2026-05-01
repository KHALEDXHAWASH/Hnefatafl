class Board:
    def __init__(self):
        self.size = 11
        self.center = (5, 5)
        self.corners = [(0, 0), (0, 10), (10, 0), (10, 10)]

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

        if (newrow, newcol) == self.center and self.grid[currentrow][currentcol] != 'K':
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
        return False

    def move(self, currentrow, currentcol, newrow, newcol):
        isvalid = self.isvalidmove(currentrow, currentcol, newrow, newcol)
        if isvalid:
            self.grid[newrow][newcol] = self.grid[currentrow][currentcol]
            self.grid[currentrow][currentcol] ='.'
            self.capturing_opponents(newrow, newcol)

            tr, tc = self.center
            if self.grid[tr][tc] != 'K':
                self.grid[tr][tc] = '.'
        else:
            print('invalid move')

    def capturing_opponents(self , r , c):
        piece = self.grid[r][c]

        if piece == 'K':
            return

        enemy = 'D' if piece == 'A' else 'A'
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            r1 , c1 = r + dr, c + dc
            r2 , c2 = r + 2*dr, c + 2*dc

            if not (0 <= r1 < self.size and 0 <= c1 < self.size):
                continue

            if self.grid[r1][c1] != enemy:
                continue

            if 0 <= r2 < self.size and 0 <= c2 < self.size:
                if self.grid[r2][c2] == piece:
                    self.grid[r1][c1] = '.'

                elif (r2 , c2) == self.center or (r2 , c2) in self.corners:
                    self.grid[r1][c1] = '.'

b = Board()
b.print_board()

b.move(0, 3, 2, 3)   # attacker moves down
print("                              ")
b.print_board()