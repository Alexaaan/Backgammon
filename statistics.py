import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class GameStatistics:
    def __init__(self):
        self.stats_file = "game_stats.json"
        self.stats = self._load_stats()
        
    def _load_stats(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r") as f:
                    return json.load(f)
            except:
                return {"team1": 0, "team2": 0}
        else:
            return {"team1": 0, "team2": 0}
    
    def save_stats(self):
        with open(self.stats_file, "w") as f:
            json.dump(self.stats, f)
    
    def add_win(self, team):
        if team == 1:
            self.stats["team1"] += 1
        elif team == 2:
            self.stats["team2"] += 1
        self.save_stats()
    
    def get_win_percentages(self):
        total_games = self.stats["team1"] + self.stats["team2"]
        if total_games == 0:
            return {"team1": 0, "team2": 0}
        
        team1_pct = (self.stats["team1"] / total_games) * 100
        team2_pct = (self.stats["team2"] / total_games) * 100
        
        return {"team1": team1_pct, "team2": team2_pct}