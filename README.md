# Sudoku Game — AI-Powered Solver 🎮🧠

A fully functional Sudoku game built in Python from scratch as part of the
Artificial Intelligence Course at Alexandria University, Faculty of Engineering,
Computer and Communication Program.

The project combines a responsive playable game with a fully implemented
AI solver using Constraint Satisfaction Problem (CSP) techniques —
Backtracking Search and Arc Consistency (AC-3).

---

## 🎯 Features

### 🎮 Gameplay
- Three difficulty levels: Easy, Medium and Hard
- Dynamically generated valid puzzles for each level
- Responsive and clean UI
- Input validation — highlights incorrect entries
- Hint system to assist the player
- Timer to track solving speed

### 🤖 AI Solver — CSP Implementation
- **Backtracking Search** to validate and solve puzzles
- Guarantees every generated puzzle is solvable
- **Arc Consistency (AC-3 Algorithm)** for constraint propagation

### 🔗 Arc Consistency Details
- Sudoku modelled as a CSP:
  - **Variables:** Each cell in the 9×9 grid
  - **Domains:** Possible values {1–9} for each cell
  - **Constraints:** No repeated values in any row, column or 3×3 subgrid
- Arcs defined for every pair of connected cells (row, column, subgrid)
- **Revise operation** applied to all arcs iteratively
- Domain reduction propagated across neighbors until no further changes occur
- Grid updated whenever a cell reaches a singleton domain

### 📋 Logging System
For every arc revision, the program logs:
- The arc (Xi, Xj) being revised
- Current domain of Xi before and after revision
- Domain of Xj at time of revision
- The specific Xj value(s) that led to domain pruning
- Variables that become singleton (assigned)
- Summary of total revisions and domains pruned

---


## 🛠️ Tech Stack

- **Language:** Python 3
- **UI:** [Tkinter / Pygame — fill in what you used]
- **AI Techniques:** Backtracking, Arc Consistency (AC-3), CSP Modelling
- **Concepts:** Constraint Propagation, Domain Reduction, Revise Operation


