import numpy as np
import pandas as pd
from itertools import combinations

class BackgammonEnv:
    def __init__(self):
        self.board = np.zeros((24, 2), dtype=int)
        self.historique = pd.DataFrame(columns=["Joueur", "Départ", "Arrivée", "Dé utilisé"])
        self.bar = [0, 0]
        self.current_player = 0  # 0 pour Joueur 1, 1 pour Joueur 2
        self.reset()

    def reset(self):
        # Configuration standard simplifiée
        self.board = np.zeros((24, 2), dtype=int)
        self.board[23, 0], self.board[12, 0], self.board[7, 0], self.board[5, 0] = 2, 5, 3, 5
        self.board[0, 1], self.board[11, 1], self.board[16, 1], self.board[18, 1] = 2, 5, 3, 5
        self.bar = [0, 0]
        self.current_player = 0
        self.historique = self.historique.iloc[0:0]
        return self.board.copy()

    def roll_dice(self):
        dice = np.random.randint(1, 7, 2)
        # Gestion des doubles : si c'est un double, on retourne 4 fois la même valeur
        if dice[0] == dice[1]:
            return [int(dice[0])] * 4
        return [int(d) for d in dice]

    def valid_moves(self, dice):
        """
        Renvoie la liste des mouvements valides possibles, sous forme de tuples (source, destination, dé utilisé).
        Les numéros de cases sont en 1-indexé (1 à 24).
        Pour le bearing off :
          - Joueur 1 : destination 0 (sortie)
          - Joueur 2 : destination 25 (sortie)
        On considère ici à la fois les mouvements individuels et, si possible, la combinaison des dés.
        """
        moves = []
        # Si le joueur a des pions sur la barre, seuls les mouvements de réintroduction sont autorisés.
        if self.bar[self.current_player] > 0:
            moves = []
            for die in dice:
                if self.current_player == 0:  # Joueur 1 (blanc)
                    # Joueur 1 entre par le camp adverse (points 24 → 19), donc point = 25 - die
                    point = 25 - die
                    if 19 <= point <= 24:  # Vérifier que le point est dans la plage valide
                        if self.board[point - 1, 1] < 2:  # Vérifier que le point n'est pas bloqué par l'adversaire
                            moves.append(("bar", point, die))
                else:  # Joueur 2 (rouge)
                    # Joueur 2 entre par points 1 à 6
                    point = die
                    if 1 <= point <= 6:  # Vérifier que le point est dans la plage valide
                        if self.board[point - 1, 0] < 2:  # Vérifier que le point n'est pas bloqué par l'adversaire
                            moves.append(("bar", point, die))
            return list(set(moves))
        
        # Le reste de votre code pour les mouvements standards...
        for point in range(24):
            src = point + 1
            if self.current_player == 0 and self.board[point, 0] > 0:
                for die in dice:
                    target = src - die
                    if target >= 1 and self.board[target - 1, 1] < 2:
                        moves.append((src, target, die))
                    if target <= 0 and die == src:
                        moves.append((src, 0, die))
                if len(dice) > 1:
                    total = sum(dice)
                    target = src - total
                    if target >= 1 and self.board[target - 1, 1] < 2:
                        moves.append((src, target, total))
                    if target <= 0 and total == src:
                        moves.append((src, 0, total))
            elif self.current_player == 1 and self.board[point, 1] > 0:
                for die in dice:
                    target = src + die
                    if target <= 24 and self.board[target - 1, 0] < 2:
                        moves.append((src, target, die))
                    if target > 24 and die == (25 - src):
                        moves.append((src, 25, die))
                if len(dice) > 1:
                    total = sum(dice)
                    target = src + total
                    if target <= 24 and self.board[target - 1, 0] < 2:
                        moves.append((src, target, total))
                    if target > 24 and total == (25 - src):
                        moves.append((src, 25, total))
        moves = list(set(moves))
        moves.sort(key=lambda x: (x[0], x[1], x[2]))
        return moves

    def step_move(self, src_input, dest_input, die_used):
        """
        Exécute un mouvement donné par le joueur.
        Les entrées sont en 1-indexé, avec pour la sortie :
          - Joueur 1 : destination 0
          - Joueur 2 : destination 25
        Le paramètre 'die_used' correspond à la valeur utilisée (simple ou combinée).
        Renvoie (succès, fin_de_partie)
        """
        # Gestion des coups venant de la barre
        if src_input == "bar":
            # Réintroduction depuis la barre
            if self.current_player == 0:
                dest_idx = dest_input - 1
                if self.board[dest_idx, 1] == 1:
                    self.board[dest_idx, 1] = 0
                    self.bar[1] += 1
                elif self.board[dest_idx, 1] >= 2:
                    return False, False
                self.bar[0] -= 1
                self.board[dest_idx, 0] += 1
            else:
                dest_idx = dest_input - 1
                if self.board[dest_idx, 0] == 1:
                    self.board[dest_idx, 0] = 0
                    self.bar[0] += 1
                elif self.board[dest_idx, 0] >= 2:
                    return False, False
                self.bar[1] -= 1
                self.board[dest_idx, 1] += 1
            self.enregistrer_coup(self.current_player, "bar", dest_input, die_used)
            if self.check_win():
                return True, True
            return True, False

        # Déplacement normal
        if self.current_player == 0:
            src_idx = src_input - 1
            if dest_input == 0:  # bearing off
                if die_used != src_input:
                    return False, False
                self.board[src_idx, 0] -= 1
            else:
                dest_idx = dest_input - 1
                if self.board[dest_idx, 1] == 1:
                    self.board[dest_idx, 1] = 0
                    self.bar[1] += 1
                elif self.board[dest_idx, 1] >= 2:
                    return False, False
                if self.board[src_idx, 0] <= 0:
                    return False, False
                self.board[src_idx, 0] -= 1
                self.board[dest_idx, 0] += 1
        else:
            src_idx = src_input - 1
            if dest_input == 25:  # bearing off
                if die_used != (25 - src_input):
                    return False, False
                self.board[src_idx, 1] -= 1
            else:
                dest_idx = dest_input - 1
                if self.board[dest_idx, 0] == 1:
                    self.board[dest_idx, 0] = 0
                    self.bar[0] += 1
                elif self.board[dest_idx, 0] >= 2:
                    return False, False
                if self.board[src_idx, 1] <= 0:
                    return False, False
                self.board[src_idx, 1] -= 1
                self.board[dest_idx, 1] += 1

        self.enregistrer_coup(self.current_player, src_input, dest_input, die_used)
        if self.check_win():
            return True, True
        return True, False


    def check_win(self):
        # Un joueur gagne s'il n'a plus de pions sur le plateau
        return np.sum(self.board[:, self.current_player]) == 0

    def enregistrer_coup(self, joueur, depart, arrivee, de_utilise):
        new_entry = pd.DataFrame([[f"Joueur {joueur + 1}", depart, arrivee, de_utilise]],
                                 columns=self.historique.columns)
        self.historique = pd.concat([self.historique, new_entry], ignore_index=True)

def find_subset(remaining, target):
    """
    Cherche et retourne une liste de dés (sous-ensemble de remaining) dont la somme est égale à target.
    Si aucun sous-ensemble n'est trouvé, retourne None.
    """
    # Pour toutes les tailles possibles de combinaison
    for r in range(1, len(remaining) + 1):
        for comb in combinations(remaining, r):
            if sum(comb) == target:
                return list(comb)
    return None
