# backgammon_ai.py
import tkinter as tk
from tkinter import messagebox, scrolledtext
from backgammon_env import BackgammonEnv
from backgammon_gui import BackgammonGUI, draw_board
import time
import random

class BackgammonGUI_AI(BackgammonGUI):
    """
    Extension of BackgammonGUI for Player vs AI gameplay.
    Inherits from the regular GUI but includes AI decision making.
    """
    def __init__(self, env, db=None):
        # Call the parent constructor to set up the GUI
        super().__init__(env, db)
        
        # Override title
        self.root.title("Backgammon - Joueur vs IA")
        
        # AI-specific attributes
        self.ai_thinking_time = 1.0  # seconds to simulate AI "thinking"
        
        # Update the info label to indicate this is an AI game
        self.info_label.config(text="Mode Joueur vs IA. Cliquez sur 'Lancer les dés' pour commencer.")
        
        # Adjust the pass button text
        self.pass_button.config(text="Passer/IA joue")

    def end_turn(self):
        """Override to handle AI turns"""
        # Check for game end first
        if self.env.check_win():
            winner = self.env.current_player + 1
            messagebox.showinfo("Fin de partie", 
                               f"{'Vous avez' if winner == 1 else 'L\'IA a'} gagné !")
            self.end_game(winner)
            self.reset_game()
            return
            
        # Switch player
        self.env.current_player = 1 - self.env.current_player
        
        # If it's AI's turn (player 2)
        if self.env.current_player == 1:  # AI is player 2 (index 1)
            self.info_label.config(text="Tour de l'IA...")
            self.remaining_dice = []
            self.dice_label.config(text="Dés: []")
            self.selected_point = None
            self.valid_destinations = []
            self.redraw()
            
            # Schedule AI's turn after a short delay
            self.root.after(500, self.ai_turn)
        else:
            # Human player's turn
            self.info_label.config(text="C'est votre tour. Cliquez sur 'Lancer les dés'.")
            self.remaining_dice = []
            self.dice_label.config(text="Dés: []")
            self.selected_point = None
            self.valid_destinations = []
            self.update_valid_moves()
            self.redraw()
    
    def ai_turn(self):
        """Execute the AI's turn"""
        # Roll dice for AI
        self.remaining_dice = self.env.roll_dice()
        self.dice_label.config(text=f"Dés IA: {self.remaining_dice}")
        self.info_label.config(text=f"L'IA a obtenu {self.remaining_dice}")
        self.update_valid_moves()
        self.redraw()
        
        # Schedule the AI move selection after a short delay
        self.root.after(int(self.ai_thinking_time * 1000), self.ai_make_moves)
    
    def ai_make_moves(self):
        """AI selects and executes moves"""
        # Continue making moves until no dice remain or no valid moves
        if not self.remaining_dice or not self.valid_moves:
            self.end_turn()
            return
            
        # For simple AI, just choose a random valid move
        move = random.choice(self.valid_moves)
        src, dest, die_used = move
        
        # Highlight the move
        self.selected_point = src
        self.valid_destinations = [dest]
        self.redraw()
        
        # Execute the move after a short delay
        self.root.after(500, lambda: self.ai_execute_move(move))
    
    def ai_execute_move(self, move):
        """Execute a specific AI move"""
        src, dest, die_used = move
        success, win = self.env.step_move(src, dest, die_used)
        
        if success:
            # Record the move
            self.execute_move(move)
            
            # Update dice - improved logic for handling dice removal
            if die_used in self.remaining_dice:
                # Simple case: the exact die value was used
                self.remaining_dice.remove(die_used)
            else:
                # Complex case: combination of dice was used
                # Find which dice were used for this move
                used_dice = []
                dice_to_account_for = die_used
                
                # Try to find a combination that adds up to the used die value
                remaining_copy = self.remaining_dice.copy()
                
                # First try to find an exact match
                if die_used in remaining_copy:
                    self.remaining_dice.remove(die_used)
                    dice_to_account_for = 0
                else:
                    # Try combinations of dice
                    for d in sorted(remaining_copy, reverse=True):
                        if dice_to_account_for >= d:
                            used_dice.append(d)
                            dice_to_account_for -= d
                            remaining_copy.remove(d)
                            
                        if dice_to_account_for == 0:
                            break
                    
                    # If we found a valid combination, remove those dice
                    if dice_to_account_for == 0:
                        for d in used_dice:
                            if d in self.remaining_dice:
                                self.remaining_dice.remove(d)
                    else:
                        # Fallback: if we can't find an exact match, just remove the largest die
                        if self.remaining_dice:
                            self.remaining_dice.pop(0)  # Assuming remaining_dice is sorted
            
            # Update UI
            self.info_label.config(text=f"L'IA joue: {src} → {dest} (Dé: {die_used})")
            self.update_history()
            self.dice_label.config(text=f"Dés restants: {self.remaining_dice}")
            self.redraw()
            
            # Schedule the next AI move
            self.root.after(1000, self.ai_make_moves)
        else:
            # This shouldn't happen with proper valid move generation
            print("Error: AI attempted invalid move")
            self.end_turn()

if __name__ == '__main__':
    env = BackgammonEnv()
    app = BackgammonGUI_AI(env)
    app.run()
