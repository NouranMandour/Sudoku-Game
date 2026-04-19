import copy
from collections import deque
import random
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import sys

CELL_SIZE = 50
PADDING = 5

class SudokuCSP:
    def __init__(self, board=None):
        if board is None:
            self.board = [[0 for _ in range(9)] for _ in range(9)]
        else:
            self.board = [row[:] for row in board]
        self.domains = {}
        self.revision_count = 0
        self.domains_pruned = 0
        self.logs = []
        self.initialize_domain()

    def initialize_domain(self):
        
        for row in range(9):
            for col in range(9):
                if self.board[row][col] != 0:
                    self.domains[(row, col)] = {self.board[row][col]}
                else:
                    self.domains[(row, col)] = set(range(1, 10))

    def get_neighbors(self, cell):
        row, col = cell
        neighbors = set()
        for i in range(9):
            if i != col:
                neighbors.add((row, i))
            if i != row:
                neighbors.add((i, col))
        box_row, box_col = 3*(row//3), 3*(col//3)
        for r in range(box_row, box_row+3):
            for c in range(box_col, box_col+3):
                if (r, c) != (row, col):
                    neighbors.add((r, c))
        return neighbors

    def get_all_arcs(self):
        arcs = []
        for row in range(9):
            for col in range(9):
                cell = (row, col)
                for neighbor in self.get_neighbors(cell):
                    arcs.append((cell, neighbor))
        return arcs

    def _revise(self, xi, xj):
        
        revised = False
        domain_xi_before = self.domains[xi].copy()
        domain_xj = self.domains[xj]
        log_entry = f"\nRevising arc (X{xi}, X{xj})"
        log_entry += f"\n  Domain X{xi} before: {sorted(domain_xi_before)}"
        log_entry += f"\n  Domain X{xj}: {sorted(domain_xj)}"

        values_to_remove = set()
        for val in domain_xi_before:
            if all(val == xj_val for xj_val in domain_xj):
                values_to_remove.add(val)
        
        if values_to_remove:
            self.domains[xi] -= values_to_remove
            self.domains_pruned += len(values_to_remove)
            revised = True
            log_entry += f"\n  Removed {sorted(values_to_remove)}"
            log_entry += f"\n  Domain X{xi} after: {sorted(self.domains[xi])}"
        else:
            log_entry += "\n  No changes"

        if revised:
            self.revision_count += 1

        self.logs.append(log_entry)
        print(log_entry)
        return revised

    def ac3(self):
       
        print("\n" + "="*60)
        print("STARTING AC-3")
        print("="*60)
        queue = deque(self.get_all_arcs())
        while queue:
            xi, xj = queue.popleft()
            if self._revise(xi, xj):
                if len(self.domains[xi]) == 0:
                    print(f"Domain X{xi} empty! CSP inconsistent")
                    return False
                if len(self.domains[xi]) == 1:
                    self.board[xi[0]][xi[1]] = list(self.domains[xi])[0]
                for xk in self.get_neighbors(xi):
                    if xk != xj and len(self.domains[xk]) > 1:
                        queue.append((xk, xi))
        print("\n" + "="*60)
        print("AC-3 COMPLETE")
        print(f"Total revisions: {self.revision_count}")
        print(f"Total domains pruned: {self.domains_pruned}")
        print("="*60)
        return True

    def safe_move(self, row, col, num):
        for i in range(9):
            if self.board[row][i] == num or self.board[i][col] == num:
                return False
        box_row, box_col = 3*(row//3), 3*(col//3)
        for r in range(box_row, box_row+3):
            for c in range(box_col, box_col+3):
                if self.board[r][c] == num:
                    return False
        return True

    def _find_empty_cell_mrv(self):
        min_size = 10
        best_cell = None
        for cell, domain in self.domains.items():
            if self.board[cell[0]][cell[1]] == 0:
                size = len(domain)
                if size < min_size:
                    min_size = size
                    best_cell = cell
                    if size == 1:
                        break
        return best_cell

    def solve_backtracking(self):
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0 and len(self.domains[(r,c)]) == 0:
                    return False
        cell = self._find_empty_cell_mrv()
        if cell is None:
            return True
        row, col = cell
        possible_values = sorted(self.domains[cell])
        for val in possible_values:
            if self.safe_move(row, col, val):
                old_domain = self.domains[cell].copy()
                self.board[row][col] = val
                self.domains[cell] = {val}
                neighbors = self.get_neighbors(cell)
                backup_domains = {n: self.domains[n].copy() for n in neighbors}
                for n in neighbors:
                    if self.board[n[0]][n[1]] == 0:
                        self.domains[n].discard(val)
                if self.solve_backtracking():
                    return True
                # Backtrack
                self.board[row][col] = 0
                self.domains[cell] = old_domain
                for n in neighbors:
                    self.domains[n] = backup_domains[n]
        return False

    def solve_with_ac3(self):
        start_time = time.time()
        if not self.ac3():
            print("Puzzle inconsistent - no solution")
            return False
        # Fill singleton domains
        for cell, domain in self.domains.items():
            if len(domain) == 1:
                self.board[cell[0]][cell[1]] = list(domain)[0]
        if all(self.board[r][c] != 0 for r in range(9) for c in range(9)):
            elapsed = time.time() - start_time
            print(f"Puzzle SOLVED using AC-3 alone in {elapsed:.4f}s")
            return True
        if self.solve_backtracking():
            elapsed = time.time() - start_time
            print(f"Puzzle SOLVED using AC-3 + Backtracking in {elapsed:.4f}s")
            return True
        print("Puzzle could not be solved")
        return False

    def print_board(self):
        print("\nBoard:")
        print("┌───────┬───────┬───────┐")
        for i in range(9):
            if i > 0 and i % 3 == 0:
                print("├───────┼───────┼───────┤")
            row_str = "│"
            for j in range(9):
                if j > 0 and j % 3 == 0:
                    row_str += "│"
                val = self.board[i][j]
                row_str += f" {val if val != 0 else '.'}"
            row_str += "│"
            print(row_str)
        print("└───────┴───────┴───────┘")

    # Puzzle generator
    def generate_puzzle(self, num_filled=30):
        self.board = [[0]*9 for _ in range(9)]
        # Fill diagonal boxes
        for box in range(0,9,3):
            self._fill_box(box, box)
        self.initialize_domain()
        self.solve_backtracking()
        # Remove cells
        filled = [(r,c) for r in range(9) for c in range(9)]
        random.shuffle(filled)
        removed = 0
        while removed < (81-num_filled) and filled:
            r,c = filled.pop()
            backup = self.board[r][c]
            self.board[r][c] = 0
            temp_solver = SudokuCSP([row[:] for row in self.board])
            if temp_solver.solve_backtracking():
                removed += 1
            else:
                self.board[r][c] = backup
        self.initialize_domain()
        return self.board

    def _fill_box(self, row_start, col_start):
        numbers = list(range(1,10))
        random.shuffle(numbers)
        idx = 0
        for r in range(row_start,row_start+3):
            for c in range(col_start,col_start+3):
                self.board[r][c] = numbers[idx]
                idx += 1


class PrintLogger:
    def __init__(self, gui_app):
        self.gui_app = gui_app
    def write(self, text):
        if text.strip():
            self.gui_app.logbox.insert(tk.END, text+"\n")
            self.gui_app.logbox.see(tk.END)
    def flush(self):
        pass

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        root.title("Sudoku CSP ")
        self.grid = [[0]*9 for _ in range(9)]
        self.cells = {}
        self.selected = None
        self.solve_user_button = None

        ctrl = tk.Frame(root)
        ctrl.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        tk.Button(ctrl, text="Mode 1: AI Solving ", command=self.mode1_ai_demo).pack(side=tk.LEFT, padx=4)
        tk.Button(ctrl, text="Mode 2: User Input ", command=self.mode2_user_input).pack(side=tk.LEFT, padx=4)
        tk.Button(ctrl, text="Validate Input", command=self.validate_input).pack(side=tk.LEFT, padx=4)
        tk.Button(ctrl, text="Generate Puzzle", command=self.generate_puzzle_gui).pack(side=tk.LEFT, padx=4)

        # --- Difficulty selection ---
        difficulty_frame = tk.Frame(ctrl)
        difficulty_frame.pack(side=tk.LEFT, padx=4)
        tk.Label(difficulty_frame, text="Difficulty:").pack(side=tk.LEFT)
        self.difficulty_var = tk.StringVar(value="Easy")
        difficulty_options = ["Easy", "Intermediate", "Hard"]
        tk.OptionMenu(difficulty_frame, self.difficulty_var, *difficulty_options).pack(side=tk.LEFT)

        board_frame = tk.Frame(root)
        board_frame.pack(side=tk.LEFT, padx=10, pady=10)
        self.canvas = tk.Canvas(board_frame, width=9*CELL_SIZE+2*PADDING, height=9*CELL_SIZE+2*PADDING)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.draw_grid()

        right = tk.Frame(root)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(right, text="Solver Log:").pack(anchor="nw")
        self.logbox = scrolledtext.ScrolledText(right, width=60, height=30)
        self.logbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        entry_frame = tk.Frame(right)
        entry_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(entry_frame, text="Enter digit (1-9) then click a cell:").pack(side=tk.LEFT)
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(entry_frame, width=3, textvariable=self.entry_var)
        self.entry.pack(side=tk.LEFT, padx=4)
        tk.Button(entry_frame, text="Clear Cell", command=self.clear_selected_cell).pack(side=tk.LEFT, padx=4)

        self.generate_puzzle_gui()

   
    def draw_grid(self):
        self.canvas.delete("all")
        for r in range(9):
            for c in range(9):
                x0=PADDING+c*CELL_SIZE
                y0=PADDING+r*CELL_SIZE
                x1=x0+CELL_SIZE
                y1=y0+CELL_SIZE
                rect=self.canvas.create_rectangle(x0,y0,x1,y1,fill="white")
                txt=self.canvas.create_text(x0+CELL_SIZE/2,y0+CELL_SIZE/2,
                                            text="" if self.grid[r][c]==0 else str(self.grid[r][c]), font=("Arial",16))
                self.cells[(r,c)] = (rect, txt)
        for i in range(10):
            w=3 if i%3==0 else 1
            x=PADDING+i*CELL_SIZE
            self.canvas.create_line(x,PADDING,x,PADDING+9*CELL_SIZE,width=w)
            y=PADDING+i*CELL_SIZE
            self.canvas.create_line(PADDING,y,PADDING+9*CELL_SIZE,y,width=w)

    def update_cell(self,r,c,v):
        self.grid[r][c]=v
        _, txt=self.cells[(r,c)]
        self.canvas.itemconfigure(txt,text="" if v==0 else str(v))
        self.root.update_idletasks()

    def on_canvas_click(self,event):
        c=int((event.x-PADDING)//CELL_SIZE)
        r=int((event.y-PADDING)//CELL_SIZE)
        if 0<=r<9 and 0<=c<9:
            self.selected=(r,c)
            val=self.entry_var.get().strip()
            if val=="":
                return
            if not val.isdigit() or not (1<=int(val)<=9):
                messagebox.showwarning("Invalid","Please enter digit 1-9")
                return
            v=int(val)
            tmp_solver=SudokuCSP(self.grid)
            if not tmp_solver.safe_move(r,c,v):
                messagebox.showwarning("Constraint",f"Placing {v} at {(r+1,c+1)} violates constraints")
                return
            self.update_cell(r,c,v)

    def clear_selected_cell(self):
        if self.selected:
            self.update_cell(self.selected[0],self.selected[1],0)

    def log_to_box(self,text):
        self.logbox.insert(tk.END,text+"\n")
        self.logbox.see(tk.END)

    def clear_log(self):
        self.logbox.delete(1.0,tk.END)

    # ---------- Mode 1 ----------
    def mode1_ai_demo(self):
        self.clear_log()
        self.log_to_box("Mode 1: AI solving ...")
        
       
        solver = SudokuCSP(self.grid)  # Pass the current grid 

        def animate_solver():
            old_stdout = sys.stdout
            sys.stdout = PrintLogger(self)
            start_time = time.time()
            solver.solve_with_ac3()
            elapsed = time.time() - start_time
            sys.stdout = sys.__stdout__
            
            # Update each cell 
            for r in range(9):
                for c in range(9):
                    self.update_cell(r, c, solver.board[r][c])
                    time.sleep(0.05)
            
            self.log_to_box(f"AI completed solving. Time taken: {elapsed:.4f} seconds")
        
        # Run the solver in background thread
        threading.Thread(target=animate_solver, daemon=True).start()

    # ---------- Mode 2 ----------
    def mode2_user_input(self):
        self.clear_log() #Clear the log box
        self.log_to_box("Mode 2: Enter puzzle, then click 'Solve'.")
        self.grid=[[0]*9 for _ in range(9)] # Initialize an empty 9x9 Sudoku grid filled with zeros
        self.draw_grid()
        if self.solve_user_button is None: # create the solve button once 
            self.solve_user_button=tk.Button(self.root,text="Solve User Puzzle",command=self.solve_user_input) 
            self.solve_user_button.pack(side=tk.TOP,pady=5) # makan el button 

    def solve_user_input(self):
        self.clear_log() # Clear the log box
        self.log_to_box("Solving user puzzle with AC-3 + Backtracking...")
        solver=SudokuCSP(self.grid) # Create solver instance

        def animate_solver():
            old_stdout=sys.stdout #Save the current stdout
            sys.stdout=PrintLogger(self) # ba7otaha f log 
            start_time=time.time()
            solver.solve_with_ac3() # b run el ac3 solver 
            elapsed=time.time()-start_time
            sys.stdout=sys.__stdout__ # restore stdout 
            for r in range(9): # Update the gui grid cell by cell with the values from the solved puzzle
                for c in range(9):
                    self.update_cell(r,c,solver.board[r][c])
                    time.sleep(0.05) # delay 
            self.log_to_box(f"AI completed solving user puzzle. Time taken: {elapsed:.4f} seconds")

        threading.Thread(target=animate_solver,daemon=True).start() # the gui is more responsive 

    def generate_puzzle_gui(self):
        self.clear_log()
        self.log_to_box("Generating puzzle...")
        solver=SudokuCSP()
        diff=self.difficulty_var.get() # Read the selected difficulty level from dropmenu 
        if diff=="Easy": num_filled=40
        elif diff=="Intermediate": num_filled=30
        else: num_filled=22
        puzzle=solver.generate_puzzle(num_filled=num_filled)
        self.grid=puzzle
        self.draw_grid()
        self.log_to_box(f"Puzzle generated ({diff} ~{num_filled} cells prefilled).")

    def validate_input(self):
        self.clear_log()
        self.log_to_box("Validating input puzzle...")
        solver=SudokuCSP(self.grid)
        if solver.validate_puzzle():
            messagebox.showinfo("Validation","Input puzzle is solvable.")
        else:
            messagebox.showerror("Validation","Input puzzle is NOT solvable.")


def main():
    root=tk.Tk()
    app=SudokuGUI(root)
    root.mainloop()

if __name__=="__main__":
    main()








   