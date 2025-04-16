import os
import json
import datetime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GameDatabase:
    def __init__(self, db_path="game_data.json"):
        self.db_path = db_path
        # Initialize the database file if it doesn't exist
        if not os.path.exists(db_path):
            with open(db_path, 'w') as f:
                json.dump({"games": []}, f)
        
        # Load existing data
        with open(db_path, 'r') as f:
            self.data = json.load(f)
    
    def save_game(self, game_data):
        """
        Save a completed game to the database
        game_data should be a dictionary with:
        - player1: name of player 1
        - player2: name of player 2 (or "AI")
        - winner: 1 or 2 (player number)
        - moves: list of move objects
        - datetime: automatically added timestamp
        """
        # Add timestamp
        game_data["datetime"] = datetime.datetime.now().isoformat()
        
        # Add to data and save
        self.data["games"].append(game_data)
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_all_games(self):
        """Return all games in the database"""
        return self.data["games"]
    
    def get_games_by_player(self, player_name):
        """Return all games where the given player participated"""
        return [game for game in self.data["games"] 
                if game["player1"] == player_name or game["player2"] == player_name]
    
    def get_win_statistics(self):
        """Return win statistics for all players"""
        stats = {}
        for game in self.data["games"]:
            p1 = game["player1"]
            p2 = game["player2"]
            winner = game["winner"]
            
            for player in [p1, p2]:
                if player not in stats:
                    stats[player] = {"wins": 0, "losses": 0, "total": 0}
            
            if winner == 1:
                stats[p1]["wins"] += 1
                stats[p2]["losses"] += 1
            else:
                stats[p2]["wins"] += 1
                stats[p1]["losses"] += 1
                
            stats[p1]["total"] += 1
            stats[p2]["total"] += 1
        
        return stats
    
    def find_similar_game_positions(self, current_board_state, limit=5):
        """
        Find games that had a similar board state to the current one
        Returns the next moves and their win/loss outcome
        """
        similar_moves = []
        for game in self.data["games"]:
            for i, move in enumerate(game["moves"][:-1]):  # Skip the last move
                if self._compare_board_states(move["board_state"], current_board_state):
                    next_move = game["moves"][i+1]
                    winner = game["winner"]
                    # Determine if the move led to a win
                    current_player = move["player"]
                    led_to_win = (current_player == winner)
                    
                    similar_moves.append({
                        "move": next_move["move"],
                        "led_to_win": led_to_win
                    })
                    
                    if len(similar_moves) >= limit:
                        return similar_moves
        
        return similar_moves
    
    def _compare_board_states(self, state1, state2, similarity_threshold=0.8):
        """
        Compare two board states and return True if they are similar enough
        This is a simplified comparison - you can make it more sophisticated
        """
        # Simple implementation - check if percentage of matching positions is above threshold
        if len(state1) != len(state2):
            return False
            
        matches = sum(1 for i in range(len(state1)) if state1[i] == state2[i])
        similarity = matches / len(state1)
        return similarity >= similarity_threshold
    
    def create_win_percentage_chart(self, parent_widget):
        """
        Create a win percentage bar chart for display in a Tkinter window
        Returns the Tkinter canvas widget
        """
        stats = self.get_win_statistics()
        
        # Prepare data for plotting
        players = list(stats.keys())
        win_percentages = [stats[p]["wins"]/stats[p]["total"]*100 if stats[p]["total"] > 0 else 0 for p in players]
        
        # Create the figure
        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
        
        # Create the bar chart
        bars = ax.bar(players, win_percentages)
        
        # Add labels and formatting
        ax.set_ylabel('Win Percentage (%)')
        ax.set_title('Player Win Percentages')
        ax.set_ylim(0, 100)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        # Create a canvas to display the chart in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=parent_widget)
        canvas_widget = canvas.get_tk_widget()
        
        return canvas_widget