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
    '''''
    def inside_sandwich(self, row, col, piece):

        if piece == 'A':
            enemies = ['D', 'K']
        else:
            enemies = ['A']

        left = right = up = down = False

        if col - 1 >= 0:
            left = self.grid[row][col - 1] in enemies

        if col + 1 < self.size:
            right = self.grid[row][col + 1] in enemies

        if row - 1 >= 0:
            up = self.grid[row - 1][col] in enemies

        if row + 1 < self.size:
            down = self.grid[row + 1][col] in enemies
        return (left and right) or (up and down)
                  '''''

    def clone_board(self):
        newBoard = Board()
        newBoard.grid = [row[:] for row in self.grid]
        return newBoard

    def print_board(self):
        print("    ", end="")
        for col in range(self.size):
            print(f"{col:2}", end=" ")
        print("\n   +" + "---" * self.size + "+")
        for i, row in enumerate(self.grid):
            print(f"{i:2} |", end=" ")
            for cell in row:
                if cell == '.':
                    symbol = '·'
                elif cell == 'A':
                    symbol = 'A'
                elif cell == 'D':
                    symbol = 'D'
                elif cell == 'K':
                    symbol = 'K'
                else:
                    symbol = 'C'
                print(f"{symbol:2}", end=" ")
            print("|")
        print("   +" + "---" * self.size + "+")
        print()
    def find_king(self):
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == 'K':
                    return r, c
        return None, None

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

    def move(self, currentrow, currentcol, newrow, newcol, player):

        piece = self.grid[currentrow][currentcol]

        if player == 'A' and piece != 'A':
            print('Attackers can only move A pieces')
            return False

        if player == 'D' and piece not in ['D', 'K']:
            print('Defenders can only move D/K pieces')
            return False

        isvalid = self.isvalidmove(currentrow, currentcol, newrow, newcol)

        if isvalid:
            self.grid[newrow][newcol] = self.grid[currentrow][currentcol]
            self.grid[currentrow][currentcol] = '.'

            self.capturing_opponents(newrow, newcol)
            self.capture_king()

            return True

        print('invalid move')
        return False

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
                beyond_is_ally   = self.grid[r2][c2] == piece
                beyond_is_throne = (
                        (r2, c2) == self.center
                        and self.grid[r2][c2] == '.'
                )
                beyond_is_corner = (r2, c2) in self.corners
                if beyond_is_ally or beyond_is_throne or beyond_is_corner:
                    self.grid[r1][c1] = '.'

    def capture_king(self):

        kr, kc = self.find_king()

        if kr is None:
            return
        if (kr, kc) in self.corners:
            return
        attackers = 0

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:

            nr, nc = kr + dr, kc + dc

            if not (0 <= nr < self.size and 0 <= nc < self.size):
                attackers += 1
                continue

            if self.grid[nr][nc] == 'A':
                attackers += 1

            elif (nr, nc) == self.center:
                attackers += 1



        if kr == 0 or kr == self.size - 1 or kc == 0 or kc == self.size - 1:
            needed = 3
        else:
            needed = 4

        if (kr, kc) in self.corners:
            needed = 2

        if attackers >= needed:
            self.grid[kr][kc] = '.'

    def get_winner(self):
        kr, kc = self.find_king()

        if kr is None:
            return 'A'

        if (kr, kc) in self.corners:
            return 'D'

        return None

    def game_end(self):
        return self.get_winner() is not None

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
                        """""
                        if self.grid[nr][nc] != '.':
                            break
                        """""
                        nr += dr
                        nc += dc
        return moves

    def simulate_move(self,move):
        r1, c1 , r2, c2 = move

        newBoard = self.clone_board()
        piece = newBoard.grid[r1][c1]

        newBoard.grid[r2][c2] = piece
        newBoard.grid[r1][c1] = '.'

        newBoard.capturing_opponents(r2, c2)
        newBoard.capture_king()

        return newBoard

    def eval(self):
        kr, kc = self.find_king()

        if kr is None:
            return 10000
        if (kr, kc) in self.corners:
            return -10000

        attacker_count = 0
        defender_count = 0

        for r in range(self.size):
            for c in range(self.size):
                p = self.grid[r][c]
                if p == 'A':
                    attacker_count += 1
                elif p == 'D':
                    defender_count += 1

        score = (attacker_count - defender_count) * 10

        min_corner_dist = min(abs(kr - cr) + abs(kc - cc) for cr, cc in self.corners)
        score += min_corner_dist * 5

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = kr + dr, kc + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                if self.grid[nr][nc] == 'A':
                    score += 15
        return score



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


# controller....
def get_int_input(prompt, valid):
    while True:
        try:
            val = int(input(prompt))
            if val in valid:
                return val
        except ValueError:
            pass
        print(f"  Please enter one of: {valid}")


def get_str_input(prompt, valid):
    while True:
        val = input(prompt).strip().upper()
        if val in valid:
            return val
        print(f"  Please enter one of: {valid}")



def choose_difficulty():

    print('Choose Difficulty')
    print('1. Easy')
    print('2. Medium')
    print('3. Hard')

    choice = get_int_input('Enter choice: ', [1, 2, 3])

    if choice == 1:
        return 1

    if choice == 2:
        return 3

    return 5

def play_game():

    board = Board()

    difficulty = choose_difficulty()

    human = get_str_input('Choose side (A/D): ', ['A', 'D'])

    ai = 'D' if human == 'A' else 'A'

    current = 'A'

    while not board.game_end():

        board.print_board()

        if current == human:

            print(f'Human Turn ({human})')

            while True:

                try:
                    r1 = int(input('From Row: '))
                    c1 = int(input('From Col: '))
                    r2 = int(input('To Row: '))
                    c2 = int(input('To Col: '))

                    success = board.move(r1, c1, r2, c2, human)

                    if success:
                        break

                except:
                    print('Invalid Input')

        else:

            print('Computer Thinking...')

            move = board.best_move(difficulty, ai)

            if move is None:
                print('No possible moves')
                break

            r1, c1, r2, c2 = move

            print(f'Computer Move: ({r1},{c1}) -> ({r2},{c2})')

            board.move(r1, c1, r2, c2, ai)

        if current == 'A':
            current = 'D'
        else:
            current = 'A'

    board.print_board()

    winner = board.get_winner()

    if winner == 'A':
        print('Attackers Win!')
    else:
        print('Defenders Win!')
b = Board()
b.print_board()
if __name__ == "__main__":
    play_game()
