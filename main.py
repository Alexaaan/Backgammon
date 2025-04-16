import tkinter as tk
from tkinter import messagebox, ttk
from backgammon_env import BackgammonEnv
from backgammon_gui import BackgammonGUI  # Mode Joueur vs Joueur (votre version existante)
from backgammon_ai import BackgammonGUI_AI  # Mode Joueur vs IA
from game_database import GameDatabase


class MainMenu:
    def __init__(self, root):
        self.root = root
        self.db = GameDatabase()  # Initialize database
        root.title("Backgammon - Menu Principal")
        root.geometry("800x600")  # Set a larger default size
        self.frame = tk.Frame(root, padx=20, pady=20)
        self.frame.pack(expand=True)
        
        self.title_label = tk.Label(self.frame, text="Backgammon", font=("Arial", 32))
        self.title_label.pack(pady=20)
        
        self.jouer_button = tk.Button(self.frame, text="Jouer", font=("Arial", 20), command=self.open_mode_selection)
        self.jouer_button.pack(pady=10)
        
        self.stats_button = tk.Button(self.frame, text="Statistiques", font=("Arial", 20), command=self.open_statistics)
        self.stats_button.pack(pady=10)
        
        self.quitter_button = tk.Button(self.frame, text="Quitter", font=("Arial", 20), command=root.quit)
        self.quitter_button.pack(pady=10)

    def open_mode_selection(self):
        # Détruire le menu principal pour afficher la sélection de mode
        self.frame.destroy()
        ModeSelection(self.root, self.db)
    
    def open_statistics(self):
        # Ouvre la fenêtre de statistiques
        self.frame.destroy()
        StatisticsView(self.root, self.db)


class ModeSelection:
    def __init__(self, root, db):
        self.root = root
        self.db = db
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
        
        self.back_button = tk.Button(self.frame, text="Retour", font=("Arial", 16), command=self.back_to_menu)
        self.back_button.pack(pady=20)

    def back_to_menu(self):
        self.frame.destroy()
        MainMenu(self.root)

    def launch_pvp(self):
        # Ouvrir une boîte de dialogue pour les noms des joueurs
        player_names = PlayerNameDialog(self.root).get_player_names()
        if not player_names:  # Dialog was cancelled
            return
            
        # Lancer le mode Joueur vs Joueur
        self.root.destroy()  # Ferme la fenêtre du menu
        env = BackgammonEnv()
        env.reset()
        env.player_names = player_names  # Store player names
        gui = BackgammonGUI(env, self.db)  # Pass database to GUI
        gui.run()  # Lancement de l'interface de jeu PvP

    def launch_pve(self):
        # Ouvrir une boîte de dialogue pour le nom du joueur
        player_name = PlayerNameDialog(self.root, ai_mode=True).get_player_names()
        if not player_name:  # Dialog was cancelled
            return
            
        # Lancer le mode Joueur vs IA
        self.root.destroy()
        env = BackgammonEnv()
        env.reset()
        env.player_names = [player_name[0], "IA"]  # Player vs AI
        gui_ai = BackgammonGUI_AI(env, self.db)  # Pass database to GUI
        gui_ai.run()
    
    def launch_morden(self):
        # Similaire au mode PvP mais avec l'interface moderne
        player_names = PlayerNameDialog(self.root).get_player_names()
        if not player_names:  # Dialog was cancelled
            return
            
        # À implémenter selon votre besoin
        # ...


class StatisticsView:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        root.title("Backgammon - Statistiques")
        self.frame = tk.Frame(root, padx=20, pady=20)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.title_label = tk.Label(self.frame, text="Statistiques des parties", font=("Arial", 28))
        self.title_label.pack(pady=20)
        
        # Création d'un notebook (onglets) pour organiser les statistiques
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet 1: Win rates
        self.win_rate_tab = tk.Frame(self.notebook)
        self.notebook.add(self.win_rate_tab, text="Taux de victoire")
        
        # Ajouter le graphique
        win_chart = self.db.create_win_percentage_chart(self.win_rate_tab)
        win_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet 2: Historique des parties
        self.history_tab = tk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="Historique")
        
        # Créer un tableau pour afficher l'historique
        self.create_game_history_table()
        
        # Bouton de retour
        self.back_button = tk.Button(self.frame, text="Retour au menu", font=("Arial", 16), command=self.back_to_menu)
        self.back_button.pack(pady=20)
    
    def create_game_history_table(self):
        # Créer un cadre pour la table avec une barre de défilement
        table_frame = tk.Frame(self.history_tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barre de défilement
        scrollbar = tk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Création du treeview (tableau)
        columns = ("Date", "Joueur 1", "Joueur 2", "Vainqueur", "Durée")
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        
        # Configuration des colonnes
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Attacher la barre de défilement
        scrollbar.config(command=self.tree.yview)
        
        # Remplir le tableau avec les données
        games = self.db.get_all_games()
        for i, game in enumerate(games):
            date = datetime.datetime.fromisoformat(game["datetime"]).strftime("%d/%m/%Y %H:%M")
            winner_name = game["player1"] if game["winner"] == 1 else game["player2"]
            
            # Calculer la durée si disponible
            duration = "N/A"
            if "duration" in game:
                duration = f"{game['duration']:.1f}s"
                
            self.tree.insert("", tk.END, values=(date, game["player1"], game["player2"], winner_name, duration))
        
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def back_to_menu(self):
        self.frame.destroy()
        MainMenu(self.root)


class PlayerNameDialog:
    def __init__(self, parent, ai_mode=False):
        self.result = None
        self.ai_mode = ai_mode
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Noms des joueurs")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_window(self.dialog, 400, 200)
        
        # Add widgets
        if not ai_mode:
            tk.Label(self.dialog, text="Nom du Joueur 1:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
            self.player1_entry = tk.Entry(self.dialog, width=20)
            self.player1_entry.grid(row=0, column=1, padx=10, pady=10)
            self.player1_entry.insert(0, "Joueur 1")
            
            tk.Label(self.dialog, text="Nom du Joueur 2:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
            self.player2_entry = tk.Entry(self.dialog, width=20)
            self.player2_entry.grid(row=1, column=1, padx=10, pady=10)
            self.player2_entry.insert(0, "Joueur 2")
        else:
            tk.Label(self.dialog, text="Votre nom:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
            self.player1_entry = tk.Entry(self.dialog, width=20)
            self.player1_entry.grid(row=0, column=1, padx=10, pady=10)
            self.player1_entry.insert(0, "Joueur")
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Annuler", command=self.on_cancel).pack(side=tk.LEFT, padx=10)
        
        # Make dialog modal
        self.dialog.wait_window()
    
    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        window.geometry('%dx%d+%d+%d' % (width, height, x, y))
    
    def on_ok(self):
        if self.ai_mode:
            self.result = [self.player1_entry.get()]
        else:
            self.result = [self.player1_entry.get(), self.player2_entry.get()]
        self.dialog.destroy()
    
    def on_cancel(self):
        self.dialog.destroy()
    
    def get_player_names(self):
        return self.result


if __name__ == "__main__":
    root = tk.Tk()
    menu = MainMenu(root)
    root.mainloop()
