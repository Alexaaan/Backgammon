import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import tkinter as tk
from tkinter import Toplevel, Text, Scrollbar, VERTICAL, RIGHT, Y, LEFT, BOTH

class GameStats:
    def __init__(self):
        self.stats_df = pd.DataFrame(columns=[
            'date', 'winner', 'duration', 'total_moves',
            'player1_captures', 'player2_captures',
            'game_mode'  # 'PvP' ou 'PvAI'
        ])
        try:
            self.load_stats()
        except FileNotFoundError:
            self.save_stats()

    def load_stats(self):
        self.stats_df = pd.read_csv('game_stats.csv')

    def save_stats(self):
        self.stats_df.to_csv('game_stats.csv', index=False)

    def add_game(self, winner, duration, total_moves, p1_captures, p2_captures, game_mode):
        new_game = pd.DataFrame([{
            'date': datetime.now(),
            'winner': f'Player {winner}',
            'duration': duration,
            'total_moves': total_moves,
            'player1_captures': p1_captures,
            'player2_captures': p2_captures,
            'game_mode': game_mode
        }])
        self.stats_df = pd.concat([self.stats_df, new_game], ignore_index=True)
        self.save_stats()

    def generate_reports(self):
        """Génère des graphiques d'analyse"""
        # Victoires par joueur
        plt.figure(figsize=(10, 6))
        sns.countplot(data=self.stats_df, x='winner')
        plt.title('Nombre de victoires par joueur')
        plt.savefig('victories.png')
        plt.close()

        # Durée moyenne des parties
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=self.stats_df, x='game_mode', y='duration')
        plt.title('Distribution des durées de partie par mode')
        plt.savefig('durations.png')
        plt.close()

        # Captures moyennes
        plt.figure(figsize=(10, 6))
        captures = pd.DataFrame({
            'Player 1': self.stats_df['player1_captures'],
            'Player 2': self.stats_df['player2_captures']
        }).melt()
        sns.boxplot(data=captures, x='variable', y='value')
        plt.title('Distribution des captures par joueur')
        plt.savefig('captures.png')
        plt.close()

    def show_stats_menu(self, root):
        """Affiche une fenêtre Tkinter avec les statistiques."""
        window = Toplevel(root)
        window.title("Statistiques des parties")
        window.geometry("600x400")

        # Zone de texte pour afficher les statistiques
        text_area = Text(window, wrap="none", font=("Arial", 12))
        scrollbar = Scrollbar(window, orient=VERTICAL, command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=RIGHT, fill=Y)
        text_area.pack(side=LEFT, fill=BOTH, expand=True)

        # Charger les statistiques et les afficher
        try:
            stats_text = self.stats_df.to_string(index=False)
            text_area.insert("1.0", stats_text)
        except Exception as e:
            text_area.insert("1.0", f"Erreur lors du chargement des statistiques : {e}")