import tkinter as tk
from tkinter import messagebox
import random
import time

class Buscaminas:
    def __init__(self, master):
        self.master = master
        self.master.title("Buscaminas")
        self.master.configure(bg="#B0E0E6")  # Fondo claro para el tablero
        self.rows = 4
        self.cols = 4
        self.mines = 1
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.mines_positions = set()
        self.game_over = False

        self.colors = {1: "blue", 2: "green", 3: "red", 4: "purple", 5: "maroon", 6: "turquoise", 7: "black", 8: "gray"}
        
        self.create_board()
        self.place_mines()

        # Botón para que la IA juegue
        self.ai_button = tk.Button(self.master, text="IA Jugar", font=("Helvetica", 12, "bold"), bg="#FF6347", fg="white", command=self.ai_play)
        self.ai_button.grid(row=self.rows, column=0, columnspan=self.cols, pady=10)

    def create_board(self):
        for i in range(self.rows):
            for j in range(self.cols):
                btn = tk.Button(self.master, width=3, height=1, font=("Helvetica", 14), bg="#ADD8E6", relief="raised")
                btn.grid(row=i, column=j, padx=1, pady=1)
                btn.bind('<Button-1>', lambda e, row=i, col=j: self.click(row, col))
                btn.bind('<Button-3>', lambda e, row=i, col=j: self.flag(row, col))
                self.buttons[i][j] = btn

    def place_mines(self):
        mines_placed = 0
        while mines_placed < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if (row, col) not in self.mines_positions:
                self.mines_positions.add((row, col))
                mines_placed += 1

    def click(self, row, col):
        if self.game_over:
            return

        btn = self.buttons[row][col]
        if btn['text'] == '🚩':
            return

        if (row, col) in self.mines_positions:
            self.game_over = True
            self.show_mines()
            messagebox.showinfo("Game Over", "¡Has perdido!")
        else:
            count = self.count_adjacent_mines(row, col)
            if count > 0:
                btn.config(text=str(count), state="disabled", disabledforeground=self.colors.get(count, "black"), bg="white")
            else:
                btn.config(text="", state="disabled", bg="lightblue")  # Color para los espacios vacíos
                self.clear_adjacent(row, col)

        if self.check_win():
            self.game_over = True
            messagebox.showinfo("Felicidades", "¡Has ganado!")

    def flag(self, row, col):
        if self.game_over:
            return

        btn = self.buttons[row][col]
        if btn['text'] == '':
            btn.config(text='🚩', fg="red", font=("Helvetica", 14, "bold"), bg="#FFFACD")  # Color amarillo para banderas
        elif btn['text'] == '🚩':
            btn.config(text='', bg="#ADD8E6")

    def count_adjacent_mines(self, row, col):
        count = 0
        for i in range(max(0, row-1), min(self.rows, row+2)):
            for j in range(max(0, col-1), min(self.cols, col+2)):
                if (i, j) in self.mines_positions:
                    count += 1
        return count

    def clear_adjacent(self, row, col):
        for i in range(max(0, row-1), min(self.rows, row+2)):
            for j in range(max(0, col-1), min(self.cols, col+2)):
                btn = self.buttons[i][j]
                if btn['state'] == 'normal' and btn['text'] != '🚩':
                    count = self.count_adjacent_mines(i, j)
                    if count > 0:
                        btn.config(text=str(count), state="disabled", disabledforeground=self.colors.get(count, "black"), bg="white")
                    else:
                        btn.config(text="", state="disabled", bg="lightblue")  # Color para los espacios vacíos
                        self.clear_adjacent(i, j)

    def show_mines(self):
        for row, col in self.mines_positions:
            self.buttons[row][col].config(text="💣", fg="black", bg="red")

    def check_win(self):
        for i in range(self.rows):
            for j in range(self.cols):
                btn = self.buttons[i][j]
                if btn['state'] == 'normal' and (i, j) not in self.mines_positions:
                    return False
        return True

    # IA que analiza y marca minas
    def ai_play(self):
        while not self.game_over:
            played = False

            # Primero marca las posibles minas
            for i in range(self.rows):
                for j in range(self.cols):
                    btn = self.buttons[i][j]
                    if btn['state'] == 'disabled' and btn['text'] and btn['text'].isdigit():
                        num_mines = int(btn['text'])
                        flagged, hidden = self.analyze_surrounding(i, j)
                        
                        # Si hay casillas ocultas igual al número de minas, marca esas casillas con banderas
                        if hidden == num_mines - flagged:
                            self.mark_flags_around(i, j)
                            played = True

            # Luego, si todas las minas alrededor de un número están marcadas, se hace clic en las casillas restantes
            for i in range(self.rows):
                for j in range(self.cols):
                    btn = self.buttons[i][j]
                    if btn['state'] == 'disabled' and btn['text'].isdigit():
                        num_mines = int(btn['text'])
                        flagged, hidden = self.analyze_surrounding(i, j)
                        
                        if flagged == num_mines:
                            self.click_safe_around(i, j)
                            played = True

            if not played:
                # Si no hay movimientos seguros, haz clic aleatorio
                self.click_random()

            self.master.update()
            time.sleep(0.5)

    def analyze_surrounding(self, row, col):
        flagged = 0
        hidden = 0
        for i in range(max(0, row-1), min(self.rows, row+2)):
            for j in range(max(0, col-1), min(self.cols, col+2)):
                btn = self.buttons[i][j]
                if btn['text'] == '🚩':
                    flagged += 1
                elif btn['state'] == 'normal':
                    hidden += 1
        return flagged, hidden

    def mark_flags_around(self, row, col):
        for i in range(max(0, row-1), min(self.rows, row+2)):
            for j in range(max(0, col-1), min(self.cols, col+2)):
                btn = self.buttons[i][j]
                if btn['state'] == 'normal' and btn['text'] == '':
                    self.flag(i, j)

    def click_safe_around(self, row, col):
        for i in range(max(0, row-1), min(self.rows, row+2)):
            for j in range(max(0, col-1), min(self.cols, col+2)):
                btn = self.buttons[i][j]
                if btn['state'] == 'normal' and btn['text'] == '':
                    self.click(i, j)

    def click_random(self):
        available_cells = [(i, j) for i in range(self.rows) for j in range(self.cols) 
                       if self.buttons[i][j]['state'] == 'normal' and self.buttons[i][j]['text'] == '']
        if available_cells:
            row, col = random.choice(available_cells)
            self.click(row, col)

if __name__ == "__main__":
    root = tk.Tk()
    game = Buscaminas(root)
    root.mainloop()
