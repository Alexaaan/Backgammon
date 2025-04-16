import random
import numpy as np
from game_database import GameDatabase

class BackgammonAI:
    def __init__(self, env, database):
        self.env = env
        self.db = database
        self.player_id = 2  # AI is typically player 2
    
    def choose_move(self, possible_moves, dice_rolls):
        """
        Choose the best move from the possible moves
        Uses the strategy described in the requirements
        """
        if not possible_moves:
            return None
            
        # 1. Create a dictionary of possible moves with initial score 0
        move_scores = {str(move): 0 for move in possible_moves}
        
        # 2. Evaluate each move
        for move_str in move_scores:
            move = eval(move_str)  # Convert string back to move object
            score = self.evaluate_move(move, dice_rolls)
            move_scores[move_str] = score
        
        # 5. Choose the move with the best score
        best_move_str = max(move_scores, key=move_scores.get)
        best_move = eval(best_move_str)
        
        # For debugging
        print(f"AI chose move with score {move_scores[best_move_str]}")
        
        return best_move
    
    def evaluate_move(self, move, dice_rolls):
        """
        3. Function to evaluate a move and return a score
        4. Use database to improve evaluation
        """
        score = 0
        
        # Create a copy of the environment to simulate the move
        env_copy = self.env.clone()
        
        # Apply the move to the copy
        old_board = env_copy.board.copy()  # Store the board before move
        env_copy.make_move(move)
        
        # Strategic evaluation
        score += self._evaluate_strategic_position(env_copy)
        
        # Check for historical data on similar positions
        similar_moves = self.db.find_similar_game_positions(old_board)
        
        # Add score based on historical data
        for similar in similar_moves:
            if self._compare_moves(move, similar["move"]):
                score += 50 if similar["led_to_win"] else -30
        
        return score
    
    def _evaluate_strategic_position(self, env):
        """Evaluate the strategic value of a position"""
        board = env.board
        score = 0
        
        # Basic strategy evaluation
        
        # 1. Prefer moves that hit opponent's checkers
        if env.hit_occurred:
            score += 100
        
        # 2. Prefer moves that create anchors/blocks (2+ checkers)
        for i in range(24):
            # If we have 2 or more checkers on a point
            if (board[i] >= 2 and self.player_id == 1) or (board[i] <= -2 and self.player_id == 2):
                score += 10
        
        # 3. Penalize exposed single checkers (blots)
        for i in range(24):
            if (board[i] == 1 and self.player_id == 1) or (board[i] == -1 and self.player_id == 2):
                score -= 15
        
        # 4. Prefer moves toward the home board
        home_board_start = 0 if self.player_id == 1 else 18
        for i in range(6):
            pos = home_board_start + i
            # Count checkers in home board
            if (board[pos] > 0 and self.player_id == 1) or (board[pos] < 0 and self.player_id == 2):
                score += 5 * abs(board[pos])
        
        # 5. Bearing off is highly prioritized
        if env.player_can_bear_off(self.player_id):
            score += 200
            # Extra points for each checker that was beared off
            score += env.player_checkers_off(self.player_id) * 20
        
        return score
    
    def _compare_moves(self, move1, move2):
        """Compare if moves are similar enough"""
        # Simple comparison - check if source and destination are the same
        if not (move1 and move2):
            return False
            
        # Compare source and target positions
        return move1["from"] == move2["from"] and move1["to"] == move2["to"]