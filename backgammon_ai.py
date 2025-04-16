# backgammon_ai.py
import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
from backgammon_env import BackgammonEnv, find_subset
from backgammon_gui import Board,CANVAS_WIDTH, CANVAS_HEIGHT

class BackgammonGUI_AI:
    def __init__(self):
        self.env = BackgammonEnv()
        self.env.reset()
        # On considère que Joueur 1 est l'humain et Joueur 2 l'IA
        self.env.current_player = 0
        
        self.root = tk.Tk()
        self.root.title("Backgammon - Joueur vs IA")
        
        # Zone du plateau (board) en haut
        self.canvas = tk.Canvas(self.root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.pack()
        self.board = Board(self.canvas)
        self.selected_point = None
        self.valid_destinations = []
        self.remaining_dice = []
        
        # Ligne de séparation (exemple d'une ligne bleue)
        separator = tk.Frame(self.root, height=2, bg="blue")
        separator.pack(fill=tk.X, pady=5)
        
        # Zone d'actions en bas
        self.action_frame = tk.Frame(self.root)
        self.action_frame.pack(pady=5)
        
        self.info_label = tk.Label(self.action_frame, text="Cliquez sur 'Lancer les dés' pour commencer.", font=("Arial", 12))
        self.info_label.grid(row=0, column=0, columnspan=3, pady=5)
        
        self.dice_label = tk.Label(self.action_frame, text="Dés: []", font=("Arial", 12))
        self.dice_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        self.roll_button = tk.Button(self.action_frame, text="Lancer les dés", command=self.roll_dice, font=("Arial", 12))
        self.roll_button.grid(row=2, column=0, padx=5, pady=5)
        
        self.pass_button = tk.Button(self.action_frame, text="Passer", command=self.pass_turn, font=("Arial", 12))
        self.pass_button.grid(row=2, column=1, padx=5, pady=5)
        
        self.reset_button = tk.Button(self.action_frame, text="Nouvelle partie", command=self.reset_game, font=("Arial", 12))
        self.reset_button.grid(row=2, column=2, padx=5, pady=5)
        
        self.moves_listbox = tk.Listbox(self.action_frame, height=6, width=50)
        self.moves_listbox.grid(row=3, column=0, columnspan=3, pady=5)
        
        self.play_button = tk.Button(self.action_frame, text="Jouer ce coup", command=self.play_move, font=("Arial", 12))
        self.play_button.grid(row=4, column=0, columnspan=3, pady=5)
        
        self.history_label = tk.Label(self.action_frame, text="Historique des coups:", font=("Arial", 12))
        self.history_label.grid(row=5, column=0, columnspan=3, pady=(10,0))
        
        self.history_text = scrolledtext.ScrolledText(self.action_frame, width=60, height=10, font=("Arial", 10))
        self.history_text.grid(row=6, column=0, columnspan=3, pady=5)
        self.history_text.insert(tk.END, "Historique des coups:\n")
        self.history_text.config(state="disabled")
        
        # Lier le clic sur le canvas (pour l'humain)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.update_board()

    def roll_dice(self):
        self.remaining_dice = self.env.roll_dice()
        self.info_label.config(text=f"Résultat des dés: {self.remaining_dice}")
        self.dice_label.config(text=f"Dés: {self.remaining_dice}")
        self.update_valid_moves()
        self.selected_point = None
        self.valid_destinations = []
        self.update_board()
        # Si c'est le tour de l'IA, lancer l'IA après un court délai
        if self.env.current_player == 1:
            self.root.after(1000, self.ai_move)
            
    def update_valid_moves(self):
        self.valid_moves = self.env.valid_moves(self.remaining_dice)
        self.moves_listbox.delete(0, tk.END)
        for move in self.valid_moves:
            self.moves_listbox.insert(tk.END, f"{move[0]} → {move[1]} (dé: {move[2]})")
        if not self.valid_moves:
            messagebox.showinfo("Info", "Aucun coup possible. Passage automatique au joueur suivant.")
            self.pass_turn()

    def play_move(self):
        # Cette fonction est uniquement pour l'humain (Joueur 1)
        if self.env.current_player != 0:
            return  # Ignore si ce n'est pas le tour de l'humain
        selected = self.moves_listbox.curselection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un mouvement.")
            return
        move_text = self.moves_listbox.get(selected[0])
        parts = move_text.split(" → ")
        src = int(parts[0])
        dest = int(parts[1].split(" (")[0])
        die_used = int(parts[1].split(": ")[1].replace(")", ""))
        
        subset = find_subset(self.remaining_dice, die_used)
        if subset is None:
            messagebox.showerror("Erreur", "Combinaison de dés invalide.")
            return

        success, win = self.env.step_move(src, dest, die_used)
        if not success:
            messagebox.showerror("Erreur", "Mouvement invalide.")
            return

        for d in subset:
            self.remaining_dice.remove(d)

        self.update_board()
        self.update_valid_moves()
        self.update_history()

        if win:
            messagebox.showinfo("Victoire", f"Félicitations, Joueur a gagné !")
            self.root.quit()
            return

        if not self.remaining_dice:
            self.pass_turn()

    def ai_move(self):
        # Fonction simple de l'IA : choisir aléatoirement un mouvement valide
        self.update_valid_moves()
        if not self.valid_moves:
            self.pass_turn()
            return
        move = random.choice(self.valid_moves)
        src, dest, die_used = move
        subset = find_subset(self.remaining_dice, die_used)
        if subset is None:
            self.pass_turn()
            return
        for d in subset:
            self.remaining_dice.remove(d)
        success, win = self.env.step_move(src, dest, die_used)
        self.info_label.config(text=f"L'IA a joué : {src} → {dest} (dé: {die_used})")
        self.update_board()
        self.update_valid_moves()
        self.update_history()
        if win:
            messagebox.showinfo("Victoire", "L'IA a gagné !")
            self.root.quit()
            return
        if not self.remaining_dice:
            self.pass_turn()
        else:
            # Si l'IA a encore des dés à jouer, continuer après un délai
            self.root.after(1000, self.ai_move)

    def pass_turn(self):
        self.env.current_player = 1 - self.env.current_player
        self.info_label.config(text=f"Tour de Joueur {self.env.current_player + 1}. Cliquez sur 'Lancer les dés'.")
        self.remaining_dice = []
        self.dice_label.config(text="Dés: []")
        self.selected_point = None
        self.valid_destinations = []
        self.update_valid_moves()
        self.update_board()
        # Si c'est l'IA qui commence le tour, lancer l'IA automatiquement
        if self.env.current_player == 1:
            self.root.after(1000, self.ai_move)

    def reset_game(self):
        self.env.reset()
        self.env.current_player = 0
        self.remaining_dice = []
        self.selected_point = None
        self.valid_destinations = []
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", tk.END)
        self.history_text.insert(tk.END, "Historique des coups:\n")
        self.history_text.config(state="disabled")
        self.info_label.config(text="Nouvelle partie. Cliquez sur 'Lancer les dés'.")
        self.dice_label.config(text="Dés: []")
        self.update_valid_moves()
        self.update_board()

    def update_board(self):
        self.triangles_bbox = self.board.draw(self.env, self.selected_point, self.valid_destinations)

    def update_history(self):
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", tk.END)
        self.history_text.insert(tk.END, self.env.historique.to_string(index=False))
        self.history_text.config(state="disabled")

    def on_canvas_click(self, event):
        # Cette fonction ne s'active que si c'est le tour de l'humain (Joueur 1)
        if self.env.current_player != 0:
            return
        point_clicked = self.point_from_click(event.x, event.y)
        if point_clicked is None:
            self.selected_point = None
            self.valid_destinations = []
            self.info_label.config(text="Sélection annulée.")
            self.update_board()
            return

        idx = point_clicked - 1
        if self.selected_point is None:
            if self.env.board[idx, 0] > 0:
                self.selected_point = point_clicked
                self.valid_destinations = [m[1] for m in self.valid_moves if m[0] == point_clicked]
                self.info_label.config(text=f"Point {point_clicked} sélectionné. Destinations: {self.valid_destinations}.")
            else:
                self.info_label.config(text="Ce point ne contient pas de pion sélectionnable.")
        else:
            if point_clicked in self.valid_destinations:
                move = next((m for m in self.valid_moves if m[0] == self.selected_point and m[1] == point_clicked), None)
                if move:
                    src, dest, die_used = move
                    success, win = self.env.step_move(src, dest, die_used)
                    if success:
                        subset = find_subset(self.remaining_dice, die_used)
                        if subset:
                            for d in subset:
                                self.remaining_dice.remove(d)
                        self.info_label.config(text=f"Mouvement: {src} → {dest} (dé: {die_used}).")
                        self.update_history()
                        self.selected_point = None
                        self.valid_destinations = []
                        self.update_valid_moves()
                        self.dice_label.config(text=f"Dés: {self.remaining_dice}")
                        if not self.remaining_dice:
                            self.pass_turn()
                    else:
                        self.info_label.config(text="Mouvement invalide.")
            else:
                idx2 = point_clicked - 1
                if self.env.board[idx2, 0] > 0:
                    self.selected_point = point_clicked
                    self.valid_destinations = [m[1] for m in self.valid_moves if m[0] == point_clicked]
                    self.info_label.config(text=f"Nouvelle sélection: point {point_clicked}. Destinations: {self.valid_destinations}.")
                else:
                    self.selected_point = None
                    self.valid_destinations = []
                    self.info_label.config(text="Sélection annulée.")
        self.update_board()

    def point_from_click(self, x, y):
        for point, data in self.triangles_bbox.items():
            x1, y1, x2, y2 = data["bbox"]
            if x1 <= x <= x2 and y1 <= y <= y2:
                return point
        return None

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = BackgammonGUI_AI()
    app.run()
