import tkinter as tk
from tkinter import messagebox
from backgammon_env import BackgammonEnv
from backgammon_gui import BackgammonGUI  # Mode Joueur vs Joueur (votre version existante)
from backgammon_ai import BackgammonGUI_AI  # Mode Joueur vs IA
from moder_backgammon import ModernBackgammonGUI

class MainMenu:
    def __init__(self, root):
        self.root = root
        root.title("Backgammon - Menu Principal")
        self.frame = tk.Frame(root, padx=20, pady=20)
        self.frame.pack(expand=True)
        
        self.title_label = tk.Label(self.frame, text="Backgammon", font=("Arial", 32))
        self.title_label.pack(pady=20)
        
        self.jouer_button = tk.Button(self.frame, text="Jouer", font=("Arial", 20), command=self.open_mode_selection)
        self.jouer_button.pack(pady=10)
        
        self.quitter_button = tk.Button(self.frame, text="Quitter", font=("Arial", 20), command=root.quit)
        self.quitter_button.pack(pady=10)

    def open_mode_selection(self):
        # Détruire le menu principal pour afficher la sélection de mode
        self.frame.destroy()
        ModeSelection(self.root)

class ModeSelection:
    def __init__(self, root):
        self.root = root
        root.title("Backgammon - Choix du mode")
        self.frame = tk.Frame(root, padx=20, pady=20)
        self.frame.pack(expand=True)
        
        self.label = tk.Label(self.frame, text="Choisissez le mode de jeu", font=("Arial", 28))
        self.label.pack(pady=20)
        
        self.pvp_button = tk.Button(self.frame, text="Joueur vs Joueur", font=("Arial", 20), command=self.launch_pvp)
        self.pvp_button.pack(pady=10)
        
        self.pvai_button = tk.Button(self.frame, text="Joueur vs IA", font=("Arial", 20), command=self.launch_pve)
        self.pvai_button.pack(pady=10)

        self.pvaia_button = tk.Button(self.frame, text="Joueur vs Joueur MODERN", font=("Arial", 20), command=self.launch_morden)
        self.pvaia_button.pack(pady=10)


    def launch_pvp(self):
        # Lancer le mode Joueur vs Joueur
        self.root.destroy()  # Ferme la fenêtre du menu
        env = BackgammonEnv()
        env.reset()
        gui = BackgammonGUI(env)
        gui.run()  # Lancement de l'interface de jeu PvP

    def launch_pve(self):
        # Lancer le mode Joueur vs IA
        self.root.destroy()
        env = BackgammonEnv()
        env.reset()
        gui_ai = BackgammonGUI_AI(env)
        gui_ai.run()
    def launch_morden(self):
        #bogoos mode
        self.root.destroy()
        env = BackgammonEnv()
        env.reset()
        guir = ModernBackgammonGUI(env)
        guir.run()

if __name__ == "__main__":
    root = tk.Tk()
    menu = MainMenu(root)
    root.mainloop()
