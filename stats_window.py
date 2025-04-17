import tkinter as tk
from tkinter import ttk
from statistics import GameStatistics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StatsWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Statistiques des parties")
        self.window.geometry("600x500")
        self.window.resizable(False, False)
        
        self.stats = GameStatistics()
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principale
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Statistiques de victoire", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame pour le graphique
        graph_frame = ttk.Frame(main_frame)
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Création du graphique
        self.create_graph(graph_frame)
        
        # Informations textuelles
        stats_data = self.stats.get_win_percentages()
        total_games = self.stats.stats["team1"] + self.stats.stats["team2"]
        
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text=f"Nombre total de parties: {total_games}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Équipe 1: {self.stats.stats['team1']} victoires ({stats_data['team1']:.1f}%)").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Équipe 2: {self.stats.stats['team2']} victoires ({stats_data['team2']:.1f}%)").pack(anchor=tk.W)
        
        # Bouton fermer
        ttk.Button(main_frame, text="Fermer", command=self.window.destroy).pack(pady=10)
    
    def create_graph(self, parent):
        # Création de la figure matplotlib
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('#f0f0f0')
        
        # Données pour le graphique
        win_pct = self.stats.get_win_percentages()
        teams = ["Équipe 1", "Équipe 2"]
        percentages = [win_pct["team1"], win_pct["team2"]]
        colors = ['#3498db', '#e74c3c']
        
        # Création du graphique en barres
        bars = ax.bar(teams, percentages, color=colors, width=0.6)
        
        # Ajout des pourcentages sur les barres
        for bar, pct in zip(bars, percentages):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{pct:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Personnalisation du graphique
        ax.set_ylim(0, 100)
        ax.set_ylabel('Pourcentage de victoire (%)')
        ax.set_title('Pourcentage de victoire par équipe', fontsize=14, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Intégration du graphique dans Tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)