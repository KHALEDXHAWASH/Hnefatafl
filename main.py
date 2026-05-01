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

    def clone_board(self):
        newBoard = Board()
        newBoard.grid = [row[:] for row in self.grid]
        return newBoard

    def print_board(self):
        for row in self.grid:
            print(' '.join(row))

    def isvalidmove(self, currentrow, currentcol, newrow, newcol):
        step = 1

        piece=self.grid[currentrow][currentcol]

        if piece == '.' or piece == 'C':
            return False

        if newrow < 0 or newcol < 0 or newrow >= self.size or newcol >= self.size:
            return False

        if (newrow, newcol) in self.corners:
            if piece != 'K':
                return False
        else:
            if self.grid[newrow][newcol] != '.':
                return False

        if (newrow, newcol) == self.center and piece != 'K':
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

    def get_all_moves(self, player):
        moves=[]

        for r in range(self.size):
            for c in range(self.size):
                piece = self.grid[r][c]

                if player == 'A' and piece != 'A':
                    continue
                if player== "D" and piece not in ['D','K']:
                    continue

                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

                for dr, dc in directions:
                    nr, nc = r + dr, c + dc

                    while 0 <= nr < self.size and 0 <= nc < self.size:

                        if not self.isvalidmove(r,c,nr,nc):
                            break

                        moves.append((r,c,nr, nc))

                        if self.grid[nr][nc] != '.':
                            break

                        nr+=dr
                        nc+=dc

        return moves

    def simulate_move(self,move):
        r1, c1 , r2, c2 = move

        newBoard = self.clone_board()
        piece = newBoard.grid[r1][c1]

        newBoard.grid[r2][c2] = piece
        newBoard.grid[r1][c1] = '.'

        newBoard.capturing_opponents(r2, c2)

        return newBoard

    def eval(self):
        score = 0
        for r in range(self.size):
            for c in range(self.size):
                piece = self.grid[r][c]

                if piece == 'K':
                    score -=10
                elif piece=='D':
                    score -=1

                elif piece == 'A':
                    score +=1

        return score

    # AI Helper checks if game ends
    def game_end(self):
        king_exist=False

        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == 'K':
                    king_exist =True

                    if (r,c) in self.corners:
                        return True  # Defender wins

        if not king_exist:
            return True # Attacker wins

        return False

    def alphabeta(self, depth, alpha, beta, maxmin):
        if depth==0 or self.game_end()==True:
            return self.eval()

        if maxmin: # Maximizing
            value = float('-inf')

            for move in self.get_all_moves('A'):
                child = self.simulate_move(move)
                value = max(value, child.alphabeta(depth-1, alpha, beta, False))
                alpha = max(alpha, value)

                if beta <= alpha:
                    break

            return value

        else: # Minimizing
            value = float('inf')

            for move in self.get_all_moves('D'):
                child = self.simulate_move(move)
                value = min(value, child.alphabeta(depth-1, alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha:
                    break

            return value

    def best_move(self, depth, player):
        best = None

        if player == 'A':
            best_val = float('-inf')

            for move in self.get_all_moves('A'):
                child = self.simulate_move(move)
                val = child.alphabeta( depth - 1, float('-inf'), float('inf'), False)

                if val > best_val:
                    best_val = val
                    best = move

        else:
            best_val = float('inf')

            for move in self.get_all_moves('D'):
                child = self.simulate_move(move)
                val = child.alphabeta( depth - 1, float('-inf'), float('inf'), True)

                if val < best_val:
                    best_val = val
                    best = move

        return best




b = Board()
b.print_board()

b.move(0, 3, 2, 3)   # attacker moves down
print("                              ")
b.print_board()
