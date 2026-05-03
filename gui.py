import tkinter as tk
from tkinter import messagebox, simpledialog
from pyswip import Prolog
import threading


class HnefataflGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hnefatafl - Viking Chess")

        # Configure the grid for expansion
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Initialize Prolog
        self.prolog = Prolog()
        try:
            self.prolog.consult("hnefatafl.pl")
        except Exception as e:
            messagebox.showerror("Prolog Error", f"Could not load hnefatafl.pl: {e}")
            self.root.destroy()
            return

        # 1. User Choices: Difficulty and Side
        self.depth = self.ask_difficulty()
        self.human_player = self.ask_side()
        self.computer_side = 'd' if self.human_player == 'a' else 'a'

        # Game State
        self.size = 11
        self.selected_square = None
        self.current_player = 'a'  # 'a' always moves first in Hnefatafl
        self.board_data = self.get_initial_board()

        # UI Elements
        self.canvas = tk.Canvas(root, bg="#333333")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Bindings
        self.canvas.bind("<Button-1>", self.on_square_click)
        self.canvas.bind("<Configure>", lambda e: self.draw_board())

        # If the computer is the Attacker, it needs to move first
        if self.computer_side == 'a':
            self.root.after(1000, self.computer_move)

        self.root.after(100, self.draw_board)

    def ask_difficulty(self):
        choice = simpledialog.askinteger(
            "Difficulty",
            "Choose Difficulty Level:\n1 - Easy (Depth 1)\n2 - Medium (Depth 3)\n3 - Hard (Depth 5)",
            parent=self.root, minvalue=1, maxvalue=3
        )
        mapping = {1: 1, 2: 3, 3: 5}
        return mapping.get(choice, 1)

    def ask_side(self):
        """Asks the user to choose Attacker or Defender."""
        choice = simpledialog.askstring(
            "Side Selection",
            "Choose your side:\n'a' - Attacker (Moves First)\n'd' - Defender (Protects King)",
            parent=self.root
        )
        if choice and choice.lower().strip() in ['a', 'd']:
            return choice.lower().strip()
        return 'a'  # Default to attacker

    def get_initial_board(self):
        result = list(self.prolog.query("initial_board(B)"))
        return result[0]['B']

    def draw_board(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self.cell_size = min(w, h) // self.size

        colors = {'e': "#f0d9b5", 'a': "#cc0000", 'd': "#ffffff", 'k': "#ffcc00", 'c': "#8b4513"}

        for r in range(self.size):
            for c in range(self.size):
                piece = self.board_data[r][c]
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size

                bg = "#b58863" if (r + c) % 2 == 0 else "#f0d9b5"
                if (r, c) in [(0, 0), (0, 10), (10, 0), (10, 10), (5, 5)]:
                    bg = "#4d3d2d"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg, outline="black")

                if self.selected_square == (r, c):
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="cyan", width=4)

                if piece in ['a', 'd', 'k']:
                    color = colors[piece]
                    padding = self.cell_size // 8
                    self.canvas.create_oval(x1 + padding, y1 + padding, x2 - padding, y2 - padding, fill=color,
                                            outline="black")

    def on_square_click(self, event):
        # Ignore clicks if it's not the human's turn
        if self.current_player != self.human_player:
            return

        col = event.x // self.cell_size
        row = event.y // self.cell_size

        if row >= self.size or col >= self.size: return

        if self.selected_square:
            start_r, start_c = self.selected_square
            if (start_r, start_c) != (row, col):
                self.execute_move(start_r, start_c, row, col)
            self.selected_square = None
        else:
            piece = self.board_data[row][col]
            # Verify the human is clicking their own pieces
            if (self.human_player == 'a' and piece == 'a') or \
                    (self.human_player == 'd' and piece in ['d', 'k']):
                self.selected_square = (row, col)

        self.draw_board()

    def execute_move(self, r, c, nr, nc):
        board_str = str(self.board_data).replace("'", "")
        query = f"isvalidmove({board_str}, {r}, {c}, {nr}, {nc})"

        if list(self.prolog.query(query)):
            sim_query = f"simulate_move({board_str}, {r}, {c}, {nr}, {nc}, NewBoard)"
            result = list(self.prolog.query(sim_query))
            self.board_data = result[0]['NewBoard']

            self.current_player = 'd' if self.current_player == 'a' else 'a'
            self.draw_board()

            if not self.check_game_over():
                if self.current_player == self.computer_side:
                    self.root.after(200, self.computer_move)
        else:
            messagebox.showwarning("Invalid Move", "Illegal move!")

    def computer_move(self):
        self.canvas.config(cursor="watch")

        def ai_task():
            board_str = str(self.board_data).replace("'", "")
            query = f"best_move({board_str}, {self.depth}, {self.computer_side}, (R, C, NR, NC))"
            try:
                result = list(self.prolog.query(query))
                self.root.after(0, self.process_ai_result, result)
            except Exception as e:
                print(f"AI Error: {e}")

        threading.Thread(target=ai_task, daemon=True).start()

    def process_ai_result(self, result):
        self.canvas.config(cursor="")
        if result and 'R' in result[0]:
            move = result[0]
            self.execute_move(move['R'], move['C'], move['NR'], move['NC'])
        else:
            messagebox.showinfo("Game Over", "Computer has no valid moves!")

    def check_game_over(self):
        board_str = str(self.board_data).replace("'", "")
        res = list(self.prolog.query(f"get_winner({board_str}, Winner)"))
        if res and res[0]['Winner'] != 'none':
            winner = "Attackers" if res[0]['Winner'] == 'a' else "Defenders"
            messagebox.showinfo("Victory", f"{winner} win!")
            self.root.destroy()
            return True
        return False


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x700")
    gui = HnefataflGUI(root)
    root.mainloop()