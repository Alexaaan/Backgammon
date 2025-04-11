import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from itertools import chain
from backgammon_env import BackgammonEnv

# --- Canvas Parameters ---
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 500
BAR_WIDTH = 40

# Modern Color Scheme
BOARD_BG_COLOR = "#2C3E50"  # Dark blue-gray
TRIANGLE_RED = "#E74C3C"    # Flat red
TRIANGLE_WHITE = "#ECF0F1"  # Light gray
BAR_COLOR = "#34495E"       # Darker blue-gray
BORDER_COLOR = "#7F8C8D"    # Medium gray

# Checker Colors
PLAYER1_COLOR = "#F1C40F"   # Golden yellow
PLAYER2_COLOR = "#9B59B6"   # Purple

# Highlight Colors
HIGHLIGHT_COLOR = "#2ECC71"  # Emerald green
SELECTED_COLOR = "#3498DB"   # Blue

# Checker Parameters
CHECKER_RADIUS = 15
CHECKER_SPACING = 27

# Calculate quadrant widths
left_quadrant_width = (CANVAS_WIDTH - BAR_WIDTH) / 2
right_quadrant_width = left_quadrant_width

class ModernBoard:
    def __init__(self, canvas):
        self.canvas = canvas
        
    def draw(self, env, selected_point=None, valid_destinations=None):
        return draw_board(self.canvas, env, selected_point, valid_destinations)

def get_triangle_for_point(point):
    """Calculate triangle coordinates and properties for a given point."""
    # [Previous get_triangle_for_point implementation remains the same]
    if 1 <= point <= 6:
        is_bottom = True
        ordre = 6 - point
        tri_width = right_quadrant_width / 6
        x0 = CANVAS_WIDTH - right_quadrant_width
        x1 = x0 + ordre * tri_width
        x2 = x1 + tri_width
        base_y = CANVAS_HEIGHT
        tip_y = CANVAS_HEIGHT / 2
    elif 7 <= point <= 12:
        is_bottom = True
        ordre = 12 - point
        tri_width = left_quadrant_width / 6
        x0 = 0
        x1 = x0 + ordre * tri_width
        x2 = x1 + tri_width
        base_y = CANVAS_HEIGHT
        tip_y = CANVAS_HEIGHT / 2
    elif 13 <= point <= 18:
        is_bottom = False
        ordre = point - 13
        tri_width = left_quadrant_width / 6
        x0 = 0
        x1 = x0 + ordre * tri_width
        x2 = x1 + tri_width
        base_y = 0
        tip_y = CANVAS_HEIGHT / 2
    elif 19 <= point <= 24:
        is_bottom = False
        ordre = point - 19
        tri_width = right_quadrant_width / 6
        x0 = CANVAS_WIDTH - right_quadrant_width
        x1 = x0 + ordre * tri_width
        x2 = x1 + tri_width
        base_y = 0
        tip_y = CANVAS_HEIGHT / 2
    else:
        raise ValueError("Point must be between 1 and 24")
    return {"x1": x1, "x2": x2, "base_y": base_y, "tip_y": tip_y, "is_bottom": is_bottom, "ordre": ordre}

def draw_triangle(canvas, point, highlight=False):
    """Draw a triangle with modern styling."""
    coords = get_triangle_for_point(point)
    x1, x2 = coords["x1"], coords["x2"]
    base_y, tip_y = coords["base_y"], coords["tip_y"]
    is_bottom = coords["is_bottom"]
    ordre = coords["ordre"]
    
    pts = [x1, base_y, x2, base_y, (x1+x2)/2, tip_y]
    color = TRIANGLE_RED if (ordre % 2 == 0) else TRIANGLE_WHITE
    
    # Draw triangle with border
    canvas.create_polygon(pts, fill=color, outline=BORDER_COLOR, width=1)
    
    # Add point number with shadow effect
    center_x = (x1 + x2) / 2
    if is_bottom:
        text_y = base_y - 15
    else:
        text_y = base_y + 15
        
    # Draw text shadow
    canvas.create_text(center_x+1, text_y+1, text=str(point), 
                      fill="#2C3E50", font=("Helvetica", 12, "bold"))
    # Draw main text
    canvas.create_text(center_x, text_y, text=str(point), 
                      fill="#34495E", font=("Helvetica", 12, "bold"))
    
    if highlight:
        canvas.create_polygon(pts, fill="", outline=HIGHLIGHT_COLOR, width=3)
    
    bbox = (min(x1, (x1+x2)/2), min(base_y, tip_y),
            max(x2, (x1+x2)/2), max(base_y, tip_y))
    return center_x, coords, bbox

def draw_checkers(canvas, center_x, coords, count, player_color, offset=0):
    """Draw checkers with modern styling and shadow effects."""
    base_y = coords["base_y"]
    is_bottom = coords["is_bottom"]
    if is_bottom:
        start_y = base_y - CHECKER_RADIUS
        dy = -CHECKER_SPACING
    else:
        start_y = base_y + CHECKER_RADIUS
        dy = CHECKER_SPACING

    max_display = 5
    num_to_draw = min(count, max_display)
    
    for i in range(num_to_draw):
        y = start_y + i * dy
        # Draw shadow
        canvas.create_oval(center_x + offset - CHECKER_RADIUS + 2,
                         y - CHECKER_RADIUS + 2,
                         center_x + offset + CHECKER_RADIUS + 2,
                         y + CHECKER_RADIUS + 2,
                         fill="#2C3E50", outline="")
        # Draw checker
        canvas.create_oval(center_x + offset - CHECKER_RADIUS,
                         y - CHECKER_RADIUS,
                         center_x + offset + CHECKER_RADIUS,
                         y + CHECKER_RADIUS,
                         fill=player_color, outline=BORDER_COLOR, width=2)
        
    if count > max_display:
        canvas.create_text(center_x + offset, start_y + num_to_draw * dy,
                         text=str(count), fill="white", font=("Helvetica", 14, "bold"))

def draw_board(canvas, env, selected_point=None, valid_destinations=None):
    """Draw the complete board with modern styling."""
    canvas.delete("all")
    canvas.config(bg=BOARD_BG_COLOR)
    
    # Draw center bar with shadow effect
    bar_x1 = (CANVAS_WIDTH - BAR_WIDTH) / 2
    bar_x2 = bar_x1 + BAR_WIDTH
    canvas.create_rectangle(bar_x1+2, 2, bar_x2+2, CANVAS_HEIGHT+2,
                          fill="#2C3E50", outline="")
    canvas.create_rectangle(bar_x1, 0, bar_x2, CANVAS_HEIGHT,
                          fill=BAR_COLOR, outline=BORDER_COLOR)
    
    triangles_bbox = {}
    for point in range(1, 25):
        hl = False
        if selected_point == point or (valid_destinations and point in valid_destinations):
            hl = True
        center_x, coords, bbox = draw_triangle(canvas, point, highlight=hl)
        triangles_bbox[point] = {"coords": coords, "center_x": center_x, "bbox": bbox}
        
        idx = point - 1
        count_white = int(env.board[idx, 0])
        count_red = int(env.board[idx, 1])
        
        if count_white and not count_red:
            draw_checkers(canvas, center_x, coords, count_white, PLAYER1_COLOR)
        elif count_red and not count_white:
            draw_checkers(canvas, center_x, coords, count_red, PLAYER2_COLOR)
        elif count_white and count_red:
            draw_checkers(canvas, center_x - 10, coords, count_white, PLAYER1_COLOR)
            draw_checkers(canvas, center_x + 10, coords, count_red, PLAYER2_COLOR)
            
    return triangles_bbox

class ModernBackgammonGUI:
    def __init__(self, env):
        self.env = env
        self.root = tk.Tk()
        self.root.title("Modern Backgammon")
        self.root.configure(bg="#ECF0F1")
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Modern.TButton',
            padding=10,
            background='#3498DB',
            foreground='white',
            font=('Helvetica', 11)
        )
        self.style.configure('Info.TLabel',
            padding=8,
            background='#ECF0F1',
            font=('Helvetica', 11)
        )
        
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Canvas with border
        self.canvas_frame = ttk.Frame(self.main_frame, padding=2)
        self.canvas_frame.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        self.canvas = tk.Canvas(self.canvas_frame, 
                              width=CANVAS_WIDTH, 
                              height=CANVAS_HEIGHT,
                              highlightthickness=0)
        self.canvas.grid(row=0, column=0)
        
        # Info section
        self.info_frame = ttk.Frame(self.main_frame)
        self.info_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 20))
        
        self.info_label = ttk.Label(
            self.info_frame,
            text="Welcome to Backgammon! Click 'Roll Dice' to begin.",
            style='Info.TLabel'
        )
        self.info_label.grid(row=0, column=0, columnspan=4, pady=5)
        
        self.dice_label = ttk.Label(
            self.info_frame,
            text="Dice: []",
            style='Info.TLabel'
        )
        self.dice_label.grid(row=1, column=0, columnspan=4, pady=5)
        
        # Button container
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 20))
        
        # Modern styled buttons
        self.roll_button = ttk.Button(
            self.button_frame,
            text="Roll Dice",
            command=self.roll_dice,
            style='Modern.TButton'
        )
        self.roll_button.grid(row=0, column=0, padx=5)
        
        self.pass_button = ttk.Button(
            self.button_frame,
            text="Pass Turn",
            command=self.pass_turn,
            style='Modern.TButton'
        )
        self.pass_button.grid(row=0, column=1, padx=5)
        
        self.reset_button = ttk.Button(
            self.button_frame,
            text="New Game",
            command=self.reset_game,
            style='Modern.TButton'
        )
        self.reset_button.grid(row=0, column=2, padx=5)
        
        self.close_button = ttk.Button(
            self.button_frame,
            text="Exit",
            command=self.root.destroy,
            style='Modern.TButton'
        )
        self.close_button.grid(row=0, column=3, padx=5)
        
        # History section
        self.history_frame = ttk.Frame(self.main_frame)
        self.history_frame.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=(0, 10))
        
        self.history_label = ttk.Label(
            self.history_frame,
            text="Game History",
            style='Info.TLabel'
        )
        self.history_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.history_text = scrolledtext.ScrolledText(
            self.history_frame,
            width=60,
            height=10,
            font=("Helvetica", 10),
            wrap=tk.WORD,
            background='white',
            borderwidth=1,
            relief="solid"
        )
        self.history_text.grid(row=1, column=0, sticky="nsew")
        self.history_text.insert(tk.END, "Game started...\n")
        self.history_text.config(state="disabled")
        
        # Game state variables
        self.selected_point = None
        self.valid_moves = []
        self.valid_destinations = []
        self.remaining_dice = []
        self.triangles_bbox = {}
        
        # Bind canvas click
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        self.redraw()
    
    # [All other methods remain the same as in your original code]
    def roll_dice(self):
        self.remaining_dice = self.env.roll_dice()
        self.info_label.config(text=f"Dice result: {self.remaining_dice}")
        self.dice_label.config(text=f"Dice: {self.remaining_dice}")
        self.update_valid_moves()
        self.selected_point = None
        self.valid_destinations = []
        self.redraw()

    def update_valid_moves(self):
        self.valid_moves = self.env.valid_moves(self.remaining_dice)

    def redraw(self):
        self.triangles_bbox = draw_board(self.canvas, self.env, self.selected_point, self.valid_destinations)

    def update_history(self):
        self.history_text.config(state="normal")
        if not self.env.historique.empty:
            dernier_coup = self.env.historique.iloc[-1]
            coup_str = f"{dernier_coup['Joueur']}: {dernier_coup['Départ']} -> {dernier_coup['Arrivée']} (Die: {dernier_coup['Dé utilisé']})\n"
            self.history_text.insert(tk.END, coup_str)
            self.history_text.see(tk.END)
        self.history_text.config(state="disabled")

    def pass_turn(self):
        self.info_label.config(text=f"Player {self.env.current_player + 1} passes their turn.")
        self.end_turn()

    def end_turn(self):
        if self.env.check_win():
            messagebox.showinfo("Game Over", f"Congratulations! Player {self.env.current_player + 1} wins!")
            self.reset_game()
            return
        self.env.current_player = 1 - self.env.current_player
        self.info_label.config(text=f"Player {self.env.current_player + 1}'s turn. Click 'Roll Dice'.")
        self.remaining_dice = []
        self.dice_label.config(text="Dice: []")
        self.selected_point = None
        self.valid_destinations = []
        self.update_valid_moves()
        self.redraw()

    def point_from_click(self, x, y):
        for point, data in self.triangles_bbox.items():
            x1, y1, x2, y2 = data["bbox"]
            if x1 <= x <= x2 and y1 <= y <= y2:
                return point
        return None

    def on_canvas_click(self, event):
        if not self.remaining_dice:
            self.info_label.config(text="Please roll the dice first.")
            return
        
        point_clicked = self.point_from_click(event.x, event.y)
        if point_clicked is None:
            self.selected_point = None
            self.valid_destinations = []
            self.info_label.config(text="Selection cancelled.")
            self.redraw()
            return
        
        idx = point_clicked - 1
        if self.env.current_player == 0:
            if self.selected_point is None:
                if self.env.board[idx, 0] > 0:
                    self.selected_point = point_clicked
                    self.valid_destinations = [m[1] for m in self.valid_moves if m[0] == point_clicked]
                    self.info_label.config(text=f"Point {point_clicked} selected. Valid moves: {self.valid_destinations}")
                else:
                    self.info_label.config(text="No valid checker to select at this point.")
            else:
                if point_clicked in self.valid_destinations:
                    move = next((m for m in self.valid_moves if m[0] == self.selected_point and m[1] == point_clicked), None)
                    if move:
                        self.execute_move(move)
                else:
                    self.handle_reselection(point_clicked, idx)
        else:
            if self.selected_point is None:
                if self.env.board[idx, 1] > 0:
                    self.selected_point = point_clicked
                    self.valid_destinations = [m[1] for m in self.valid_moves if m[0] == point_clicked]
                    self.info_label.config(text=f"Point {point_clicked} selected. Valid moves: {self.valid_destinations}")
                else:
                    self.info_label.config(text="No valid checker to select at this point.")
            else:
                if point_clicked in self.valid_destinations:
                    move = next((m for m in self.valid_moves if m[0] == self.selected_point and m[1] == point_clicked), None)
                    if move:
                        self.execute_move(move)
                else:
                    self.handle_reselection(point_clicked, idx)
        self.redraw()

    def execute_move(self, move):
        src, dest, die_used = move
        success, win = self.env.step_move(src, dest, die_used)
        if success:
            if die_used in self.remaining_dice:
                self.remaining_dice.remove(die_used)
            else:
                for d in sorted(self.remaining_dice, reverse=True):
                    if die_used - d in self.remaining_dice:
                        self.remaining_dice.remove(d)
                        self.remaining_dice.remove(die_used - d)
                        break
            self.info_label.config(text=f"Move: {src} -> {dest} (Die: {die_used})")
            self.update_history()
            self.selected_point = None
            self.valid_destinations = []
            self.update_valid_moves()
            self.dice_label.config(text=f"Dice: {self.remaining_dice}")
            if not self.remaining_dice:
                self.end_turn()
        else:
            self.info_label.config(text="Invalid move.")

    def handle_reselection(self, point_clicked, idx):
        if ((self.env.current_player == 0 and self.env.board[idx, 0] > 0) or
            (self.env.current_player == 1 and self.env.board[idx, 1] > 0)):
            self.selected_point = point_clicked
            self.valid_destinations = [m[1] for m in self.valid_moves if m[0] == point_clicked]
            self.info_label.config(text=f"New selection: point {point_clicked}. Valid moves: {self.valid_destinations}")
        else:
            self.selected_point = None
            self.valid_destinations = []
            self.info_label.config(text="Selection cancelled.")

    def reset_game(self):
        self.env.reset()
        self.env.current_player = 0
        self.remaining_dice = []
        self.selected_point = None
        self.valid_destinations = []
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", tk.END)
        self.history_text.insert(tk.END, "Game started...\n")
        self.history_text.config(state="disabled")
        self.info_label.config(text="New game. Click 'Roll Dice' to begin.")
        self.dice_label.config(text="Dice: []")
        self.redraw()

    def run(self):
        self.root.mainloop()
