"""Advanced Adaptive Rock-Paper-Scissors AI.

The computer learns player patterns and adapts its strategy:
- Tracks move frequencies and sequences
- Detects patterns (repeats, cycles, alternations)
- Adjusts play strength over time
- Shows statistics and learned patterns

Usage:
  python3 RPS.py --cli          # CLI mode
  python3 RPS.py --gui          # Graphical mode (if tkinter available)
  python3 RPS.py --games 100    # Play 100 games in CLI
  python3 RPS.py --web          # Web-based GUI (browser) *best*
"""

import random
import collections
import argparse


class RPSStats:
    """Track game statistics and player patterns."""

    def __init__(self):
        self.player_moves = []
        self.computer_moves = []
        self.results = []  # 'win', 'loss', 'tie'
        self.player_freq = collections.Counter()
        self.markov_chain = collections.defaultdict(collections.Counter)  # move -> {next_move: count}
        self.markov_2order = collections.defaultdict(collections.Counter)  # (move1, move2) -> {next_move: count}
        self.computer_freq = collections.Counter()  # Track our moves too
        self.contra_chain = collections.defaultdict(int)  # Track if player counters our moves

    def record_move(self, player_move, computer_move, result):
        """Record a move and update statistics."""
        self.player_moves.append(player_move)
        self.computer_moves.append(computer_move)
        self.results.append(result)
        self.player_freq[player_move] += 1
        self.computer_freq[computer_move] += 1

        # Update Markov chain if at least 2 moves
        if len(self.player_moves) >= 2:
            prev_move = self.player_moves[-2]
            self.markov_chain[prev_move][player_move] += 1
        
        # Update 2nd-order Markov chain if at least 3 moves
        if len(self.player_moves) >= 3:
            prev_two = (self.player_moves[-3], self.player_moves[-2])
            self.markov_2order[prev_two][player_move] += 1
        
        # Track if player counters our moves (they won)
        if result == 'loss':
            self.contra_chain[computer_move] += 1

    def get_player_tendency(self):
        """Return the most frequent player move."""
        if not self.player_freq:
            return None
        return self.player_freq.most_common(1)[0][0]

    def predict_next_move(self):
        """Predict next move based on Markov chain."""
        if len(self.player_moves) < 1:
            return None
        last_move = self.player_moves[-1]
        if last_move not in self.markov_chain or not self.markov_chain[last_move]:
            return None
        most_common = self.markov_chain[last_move].most_common(1)
        if most_common:
            return most_common[0][0]
        return None

    def detect_pattern(self):
        """Detect various patterns: pure repetition, cycles (2-5 moves), pairs, triples."""
        if len(self.player_moves) < 2:
            return None
        
        # Check pure repetition (last N moves all the same)
        if len(self.player_moves) >= 2:
            if self.player_moves[-1] == self.player_moves[-2]:
                if len(self.player_moves) >= 3 and self.player_moves[-1] == self.player_moves[-3]:
                    return "pure_repeat_3"
                if len(self.player_moves) >= 4 and all(m == self.player_moves[-1] for m in self.player_moves[-4:]):
                    return "pure_repeat_4+"
                return "pure_repeat_2"
        
        # Check cyclic patterns (longer cycles: 5-move, 4-move, 3-move, 2-move)
        if len(self.player_moves) >= 10:
            recent = self.player_moves[-10:]
            if recent[0:5] == recent[5:10]:
                return "cycle_5"
        
        if len(self.player_moves) >= 8:
            recent = self.player_moves[-8:]
            if recent[0:4] == recent[4:8]:
                return "cycle_4"
        
        if len(self.player_moves) >= 6:
            recent = self.player_moves[-6:]
            if recent[0:3] == recent[3:6]:
                return "cycle_3"
        
        if len(self.player_moves) >= 4:
            recent = self.player_moves[-4:]
            if recent[0:2] == recent[2:4]:
                return "cycle_2"
        
        # Check pair patterns (RRPPSS or similar)
        if len(self.player_moves) >= 6:
            recent = self.player_moves[-6:]
            if (recent[0] == recent[1] and recent[2] == recent[3] and recent[4] == recent[5] and
                recent[0] != recent[2] and recent[2] != recent[4]):
                return "pair_pattern"
        
        # Check triple patterns (RRRPPPSSS or similar)
        if len(self.player_moves) >= 9:
            recent = self.player_moves[-9:]
            if (all(m == recent[0] for m in recent[0:3]) and
                all(m == recent[3] for m in recent[3:6]) and
                all(m == recent[6] for m in recent[6:9]) and
                recent[0] != recent[3] and recent[3] != recent[6]):
                return "triple_pattern"
        
        # Check alternation (A, B, A, B)
        if len(self.player_moves) >= 4:
            if self.player_moves[-1] == self.player_moves[-3] and self.player_moves[-2] != self.player_moves[-1]:
                if self.player_moves[-2] == self.player_moves[-4]:
                    return "alternation"
        
        return None
    
    def get_last_n_moves(self, n):
        """Get the last n moves as a list."""
        return self.player_moves[-min(n, len(self.player_moves)):]
    
    def get_second_order_prediction(self):
        """Predict using 2nd-order Markov chain (better accuracy)."""
        if len(self.player_moves) < 2:
            return None
        prev_two = (self.player_moves[-2], self.player_moves[-1])
        if prev_two not in self.markov_2order or not self.markov_2order[prev_two]:
            return None
        return self.markov_2order[prev_two].most_common(1)[0][0]
    
    def get_move_streak(self):
        """Return (move, count) of current streak, or None."""
        if not self.player_moves:
            return None, 0
        last_move = self.player_moves[-1]
        streak = 1
        for i in range(len(self.player_moves) - 2, -1, -1):
            if self.player_moves[i] == last_move:
                streak += 1
            else:
                break
        return last_move, streak
    
    def compute_pattern_confidence(self):
        """Return confidence score (0-1) of current pattern detection."""
        pattern = self.detect_pattern()
        if not pattern:
            return 0.0
        
        if "pure_repeat" in pattern:
            streak_move, streak_count = self.get_move_streak()
            return min(1.0, streak_count / 5.0)  # 5+ repeats = 100% confidence
        
        if "cycle" in pattern:
            # Check how many complete cycles
            if "cycle_2" in pattern:
                complete_cycles = len(self.player_moves) // 2
            elif "cycle_3" in pattern:
                complete_cycles = len(self.player_moves) // 3
            elif "cycle_4" in pattern:
                complete_cycles = len(self.player_moves) // 4
            elif "cycle_5" in pattern:
                complete_cycles = len(self.player_moves) // 5
            else:
                complete_cycles = 1
            return min(1.0, complete_cycles / 3.0)  # 3+ cycles = 100% confidence
        
        return 0.5  # Medium confidence for other patterns
    
    def classify_player(self):
        """Classify player as 'repetitive', 'adaptive', or 'random'."""
        if len(self.player_moves) < 5:
            return "unknown"
        
        # High repetition = repetitive
        most_common_count = self.player_freq.most_common(1)[0][1] if self.player_freq else 0
        if most_common_count / len(self.player_moves) > 0.6:
            return "repetitive"
        
        # Many correct counters to our moves = adaptive
        counter_threshold = len(self.results) * 0.4
        if sum(self.contra_chain.values()) > counter_threshold:
            return "adaptive"
        
        # Otherwise random
        return "random"
    
    def predict_next_in_cycle(self):
        """Predict next move if in a cycle pattern."""
        if len(self.player_moves) < 4:
            return None
        
        pattern = self.detect_pattern()
        
        # For pure repetition, next is same
        if pattern and "pure_repeat" in pattern:
            return self.player_moves[-1]
        
        # For cycles, predict based on cycle length
        if pattern == "cycle_5" and len(self.player_moves) >= 10:
            cycle = self.player_moves[-10:-5]
            idx = len(self.player_moves) % 5
            return cycle[idx]
        
        if pattern == "cycle_4" and len(self.player_moves) >= 8:
            cycle = self.player_moves[-8:-4]
            idx = len(self.player_moves) % 4
            return cycle[idx]
        
        if pattern == "cycle_3" and len(self.player_moves) >= 6:
            cycle = self.player_moves[-6:-3]
            idx = len(self.player_moves) % 3
            return cycle[idx % 3]
        
        if pattern == "cycle_2" and len(self.player_moves) >= 4:
            cycle = self.player_moves[-4:-2]
            idx = len(self.player_moves) % 2
            return cycle[idx % 2]
        
        # For pair patterns
        if pattern == "pair_pattern" and len(self.player_moves) >= 6:
            pairs = [self.player_moves[-6], self.player_moves[-4], self.player_moves[-2]]
            idx = (len(self.player_moves) // 2) % 3
            return pairs[idx]
        
        # For triple patterns
        if pattern == "triple_pattern" and len(self.player_moves) >= 9:
            triples = [self.player_moves[-9], self.player_moves[-6], self.player_moves[-3]]
            idx = (len(self.player_moves) // 3) % 3
            return triples[idx]
        
        return None

    def get_winrate(self):
        """Return (wins, losses, ties, total games, win%)."""
        total = len(self.results)
        if total == 0:
            return 0, 0, 0, 0, 0.0
        wins = self.results.count("win")
        losses = self.results.count("loss")
        ties = self.results.count("tie")
        win_pct = (wins / total) * 100 if total > 0 else 0
        return wins, losses, ties, total, win_pct


class AdaptiveRPS:
    """Adaptive Rock-Paper-Scissors AI."""

    MOVES = ["rock", "paper", "scissors"]
    BEATS = {"rock": "paper", "paper": "scissors", "scissors": "rock"}
    BEATEN_BY = {v: k for k, v in BEATS.items()}

    def __init__(self, learning_rate=0.5):
        self.stats = RPSStats()
        self.learning_rate = learning_rate
        self.games_played = 0

    def get_counter(self, move):
        """Get the move that beats the given move."""
        return self.BEATS[move]

    def choose_move(self):
        """Choose a computer move based on learned strategy with advanced AI."""
        games = len(self.stats.player_moves)

        # Phase 1: Earliest (first 1 move) - establish baseline
        if games == 0:
            return random.choice(self.MOVES)

        # Phase 2: Very Fast Detection (1-10 games) - aggressive early pattern exploitation
        if games < 10:
            pattern = self.stats.detect_pattern()
            pattern_conf = self.stats.compute_pattern_confidence()
            
            if pattern:
                confidence_boost = min(0.95, 0.6 + pattern_conf)  # Higher confidence based on pattern strength
                
                # Pure repetition - counter with high confidence
                if "pure_repeat" in pattern:
                    if random.random() < confidence_boost:
                        return self.get_counter(self.stats.player_moves[-1])
                
                # Cycle patterns - predict and counter
                if "cycle" in pattern:
                    predicted = self.stats.predict_next_in_cycle()
                    if predicted and random.random() < confidence_boost:
                        return self.get_counter(predicted)
                
                # Pair/triple patterns
                if "pattern" in pattern:
                    predicted = self.stats.predict_next_in_cycle()
                    if predicted and random.random() < (confidence_boost - 0.1):
                        return self.get_counter(predicted)
            
            # Try 2nd-order Markov for prediction
            if random.random() < 0.3:
                second_pred = self.stats.get_second_order_prediction()
                if second_pred:
                    return self.get_counter(second_pred)
            
            return random.choice(self.MOVES)

        # Phase 3: Fast Learning (10-30 games) - pattern + Markov hybrid
        if games < 30:
            player_type = self.stats.classify_player()
            pattern = self.stats.detect_pattern()
            pattern_conf = self.stats.compute_pattern_confidence()
            
            # For repetitive players, be very aggressive
            if player_type == "repetitive":
                if pattern:
                    if "pure_repeat" in pattern and random.random() < 0.9:
                        return self.get_counter(self.stats.player_moves[-1])
                    if "cycle" in pattern or "pattern" in pattern:
                        predicted = self.stats.predict_next_in_cycle()
                        if predicted and random.random() < 0.85:
                            return self.get_counter(predicted)
            
            # Regular pattern exploitation
            if pattern and pattern_conf > 0.4:
                if "pure_repeat" in pattern:
                    if random.random() < 0.8:
                        return self.get_counter(self.stats.player_moves[-1])
                if "cycle" in pattern or "pattern" in pattern:
                    predicted = self.stats.predict_next_in_cycle()
                    if predicted and random.random() < 0.75:
                        return self.get_counter(predicted)
            
            # Use 2nd-order Markov (superior to 1st order)
            if random.random() < 0.4:
                second_pred = self.stats.get_second_order_prediction()
                if second_pred:
                    return self.get_counter(second_pred)
            
            # Fall back to 1st-order Markov
            if random.random() < 0.3:
                predicted = self.stats.predict_next_move()
                if predicted:
                    return self.get_counter(predicted)
            
            return random.choice(self.MOVES)

        # Phase 4: Advanced Expert (30+ games) - sophisticated multi-layer strategy
        pattern = self.stats.detect_pattern()
        pattern_conf = self.stats.compute_pattern_confidence()
        player_type = self.stats.classify_player()
        
        # Patterns first (highest priority)
        if pattern and pattern_conf > 0.3:
            if "pure_repeat" in pattern:
                if random.random() < min(0.95, 0.85 + (games / 500)):
                    return self.get_counter(self.stats.player_moves[-1])
            
            if "cycle" in pattern or "pattern" in pattern:
                predicted = self.stats.predict_next_in_cycle()
                if predicted and random.random() < min(0.9, 0.8 + (games / 1000)):
                    return self.get_counter(predicted)
            
            if pattern == "alternation":
                predicted = self.stats.predict_next_move()
                if predicted and random.random() < 0.85:
                    return self.get_counter(predicted)
        
        # 2nd-order Markov for sophisticated prediction
        if random.random() < min(0.7, 0.3 + games / 200):
            second_pred = self.stats.get_second_order_prediction()
            if second_pred:
                return self.get_counter(second_pred)
        
        # 1st-order Markov fallback
        if random.random() < 0.65:
            predicted = self.stats.predict_next_move()
            if predicted:
                return self.get_counter(predicted)
        
        # For adaptive players, exploit their move counters
        if player_type == "adaptive" and random.random() < 0.4:
            # Play a move they're less likely to counter
            least_countered = min(self.MOVES, key=lambda m: self.stats.contra_chain.get(m, 0))
            return least_countered
        
        # Frequency-based counter
        tendency = self.stats.get_player_tendency()
        if tendency and random.random() < min(0.95, 0.7 + (games / 300)):
            return self.get_counter(tendency)
        
        return random.choice(self.MOVES)

    def play_round(self, player_move):
        """Play a single round. Returns result."""
        player_move = player_move.lower().strip()
        if player_move not in self.MOVES:
            return None, None, "invalid"

        computer_move = self.choose_move()
        self.games_played += 1

        if player_move == computer_move:
            result = "tie"
        elif self.get_counter(player_move) == computer_move:
            result = "loss"
        else:
            result = "win"

        self.stats.record_move(player_move, computer_move, result)
        return computer_move, result, "valid"

    def report_stats(self):
        """Print statistics and discovered patterns."""
        wins, losses, ties, total, win_pct = self.stats.get_winrate()
        print("\n" + "=" * 60)
        print(f"GAME STATS (after {total} games)")
        print("=" * 60)
        print(f"Wins:  {wins:<3} | Losses: {losses:<3} | Ties: {ties:<3}")
        print(f"Win Rate: {win_pct:.1f}%")
        print(f"Computer Win Rate: {100 - win_pct - (ties/total*100):.1f}%")

        print("\nPLAYER TENDENCIES:")
        if self.stats.player_freq:
            for move, count in self.stats.player_freq.most_common():
                pct = (count / total) * 100
                print(f"  {move.capitalize():<10} {count:>3} times ({pct:.1f}%)")

        print("\nMARKOV CHAINS (what move follows what):")
        for prev_move, next_moves in self.stats.markov_chain.items():
            if next_moves:
                most_common_next = next_moves.most_common(1)[0]
                print(f"  After {prev_move.capitalize()}: likely {most_common_next[0].capitalize()} ({most_common_next[1]}x)")

        print("\nPATTERN DETECTION:")
        if len(self.stats.player_moves) >= 2:
            pattern = self.stats.detect_pattern()
            if pattern:
                pattern_names = {
                    "pure_repeat_2": "Pure Repetition (2x)",
                    "pure_repeat_3": "Pure Repetition (3x)",
                    "pure_repeat_4+": "Pure Repetition (4+ in a row)",
                    "cycle_2": "Cycle Pattern (2-move)",
                    "cycle_3": "Cycle Pattern (3-move like RPS)",
                    "cycle_4": "Cycle Pattern (4-move)",
                    "cycle_5": "Cycle Pattern (5-move)",
                    "pair_pattern": "Pair Pattern (RRPPSS style)",
                    "triple_pattern": "Triple Pattern (RRRPPPSSS style)",
                    "alternation": "Alternation Pattern (ABAB)"
                }
                conf = self.stats.compute_pattern_confidence()
                print(f"  Detected: {pattern_names.get(pattern, pattern.upper())} (confidence: {conf:.0%})")
            else:
                print(f"  (No strong pattern detected)")
        else:
            print("  (Not enough moves to detect pattern)")
        
        print("\nPLAYER CLASSIFICATION:")
        player_type = self.stats.classify_player()
        type_desc = {
            "repetitive": "Repetitive (uses same moves often)",
            "adaptive": "Adaptive (tends to counter our moves)",
            "random": "Random (unpredictable play)",
            "unknown": "Unknown (need more data)"
        }
        print(f"  {type_desc.get(player_type, player_type)}")
        
        if self.stats.contra_chain:
            print("\nCOUNTER ANALYSIS:")
            print("  Our moves countered by opponent:")
            for move, count in sorted(self.stats.contra_chain.items(), key=lambda x: -x[1]):
                print(f"    {move.capitalize()}: {count} times")
        
        print("=" * 60 + "\n")


def cli_mode(num_games=None):
    """Play in CLI mode."""
    ai = AdaptiveRPS()

    if num_games is None:
        try:
            num_games = int(input("How many games? "))
        except ValueError:
            num_games = 10

    for i in range(num_games):
        prompt = f"Game {i + 1}/{num_games} - Enter move (rock/paper/scissors) or 'quit': "
        player_move = input(prompt).lower().strip()

        if player_move == "quit":
            break

        computer_move, result, status = ai.play_round(player_move)

        if status == "invalid":
            print("Invalid move. Try again.\n")
            continue

        print(f"  You: {player_move.capitalize():<10} | Computer: {computer_move.capitalize():<10} | Result: {result.upper()}")

        if i == num_games - 1 or player_move == "quit":
            ai.report_stats()

    print("Game over!")


def gui_mode():
    """Play in GUI mode (Tkinter)."""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except ImportError:
        print("Tkinter not available. Falling back to CLI mode.")
        cli_mode()
        return
    except Exception as e:
        print(f"Tkinter initialization failed ({type(e).__name__}: {e})")
        print("This is often a macOS Tcl/Tk compatibility issue.")
        print("Try: python3 RPS.py --web  (browser-based GUI)")
        print("Or:  python3 RPS.py --cli  (command-line mode)")
        return

    ai = AdaptiveRPS()
    root = tk.Tk()
    root.title("Adaptive Rock-Paper-Scissors AI")
    root.geometry("600x500")

    # Game frame
    game_frame = ttk.Frame(root, padding=10)
    game_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(game_frame, text="Adaptive RPS - The Computer Learns!", font=("Arial", 14, "bold")).pack(pady=10)

    # Stats frame
    stats_frame = ttk.LabelFrame(game_frame, text="Game Stats", padding=10)
    stats_frame.pack(fill=tk.X, pady=10)

    games_label = ttk.Label(stats_frame, text="Games: 0", font=("Arial", 11))
    games_label.pack(anchor=tk.W)

    winrate_label = ttk.Label(stats_frame, text="Win Rate: -", font=("Arial", 11))
    winrate_label.pack(anchor=tk.W)

    pattern_label = ttk.Label(stats_frame, text="Pattern Detected: None", font=("Arial", 11))
    pattern_label.pack(anchor=tk.W)

    # Move frame
    move_frame = ttk.LabelFrame(game_frame, text="Your Move", padding=10)
    move_frame.pack(fill=tk.X, pady=10)

    move_var = tk.StringVar(value="rock")
    for move in ["rock", "paper", "scissors"]:
        ttk.Radiobutton(move_frame, text=move.capitalize(), variable=move_var, value=move).pack(anchor=tk.W)

    # Result frame
    result_frame = ttk.LabelFrame(game_frame, text="Last Round", padding=10)
    result_frame.pack(fill=tk.X, pady=10)

    result_text = tk.Text(result_frame, height=4, width=50, state=tk.DISABLED)
    result_text.pack()

    def play_round():
        player_move = move_var.get()
        computer_move, result, status = ai.play_round(player_move)

        if status == "invalid":
            messagebox.showerror("Invalid Move", "Please select a valid move.")
            return

        # Update results
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Your Move: {player_move.capitalize()}\n")
        result_text.insert(tk.END, f"Computer: {computer_move.capitalize()}\n")
        result_text.insert(tk.END, f"Result: {result.upper()}\n\n")

        # Win/loss streak hint
        wins, losses, ties, total, win_pct = ai.stats.get_winrate()
        result_text.insert(tk.END, f"Score: {wins}W {losses}L {ties}T ({win_pct:.1f}%)")
        result_text.config(state=tk.DISABLED)

        # Update stats
        games_label.config(text=f"Games: {total}")
        winrate_label.config(text=f"Win Rate: {win_pct:.1f}%")

        pattern = ai.stats.detect_pattern()
        if pattern:
            pattern_label.config(text=f"Pattern Detected: {pattern.upper()}")
        else:
            predicted = ai.stats.predict_next_move()
            if predicted:
                pattern_label.config(text=f"AI Predicting: {predicted.capitalize()}")
            else:
                pattern_label.config(text="Pattern Detected: None")

    ttk.Button(game_frame, text="PLAY", command=play_round).pack(pady=10)

    def show_full_stats():
        ai.report_stats()
        messagebox.showinfo("Full Statistics", "Check console for detailed statistics.")

    ttk.Button(game_frame, text="Show Stats", command=show_full_stats).pack()

    root.mainloop()


def web_mode(port=8765):
    """Play in web browser mode."""
    import http.server
    import socketserver
    import threading
    import webbrowser

    html_content = '''
<html>
<head>
    <meta charset="utf-8">
    <title>Adaptive RPS</title>
    <style>
        * { font-family: Arial, sans-serif; }
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
        h1 { text-align: center; color: #333; margin-top: 0; }
        .stats { background: #f0f0f0; padding: 15px; border-radius: 8px; margin: 20px 0; }
        .stat-line { margin: 8px 0; font-weight: 600; }
        .moves { display: flex; gap: 10px; justify-content: center; margin: 20px 0; }
        button { padding: 15px 25px; font-size: 16px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; transition: background 0.3s; }
        button:hover { background: #764ba2; }
        button.active { background: #28a745; }
        .result { background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; text-align: center; font-weight: 600; min-height: 60px; }
        .result.loss { background: #ffebee; }
        .result.tie { background: #fff3e0; }
        .trends { font-size: 12px; color: #666; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚔️ Adaptive Rock-Paper-Scissors</h1>
        <div class="stats">
            <div class="stat-line">Your Win Rate: <span id="winrate">-</span></div>
            <div class="stat-line">Computer Win Rate: <span id="compwin">-</span></div>
            <div class="stat-line" id="pattern">Pattern: Analyzing...</div>
        </div>
        <p style="text-align: center; color: #666;">Choose your move:</p>
        <div class="moves">
            <button onclick="play(\'rock\')" id="btn-rock">🪨 Rock</button>
            <button onclick="play(\'paper\')" id="btn-paper">📄 Paper</button>
            <button onclick="play(\'scissors\')" id="btn-scissors">✂️ Scissors</button>
        </div>
        <div class="result" id="result">Ready to play. Choose a move!</div>
        <div class="trends" id="trends"></div>
        <p style="text-align: center; margin-top: 30px;"><button onclick="resetGame()" style="background: #999;">Reset</button></p>
    </div>
    <script>
        let gameState = { games: [], stats: { player_freq: {}, computer_freq: {}, markov: {}, pattern: null } };

        async function play(move) {
            try {
                const response = await fetch("/api/play", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ move }) });
                const data = await response.json();
                updateUI(data);
            } catch (e) {
                document.getElementById("result").innerHTML = "Error: " + e.message;
            }
        }

        function updateUI(data) {
            gameState = data;
            const total = data.stats.total;
            if (total === 0) return;
            const wins = data.stats.wins;
            const losses = data.stats.losses;
            const ties = data.stats.ties;
            const playerWinPct = (wins / total * 100).toFixed(1);
            const computerWinPct = (losses / total * 100).toFixed(1);
            document.getElementById("winrate").textContent = playerWinPct + "%";
            document.getElementById("compwin").textContent = computerWinPct + "%";
            document.getElementById("pattern").textContent = "Pattern: " + (data.stats.pattern || "None detected");

            const lastRound = data.games[data.games.length - 1];
            const resultDiv = document.getElementById("result");
            resultDiv.className = "result " + lastRound.result;
            resultDiv.innerHTML = `You: <strong>${lastRound.player}</strong><br>Computer: <strong>${lastRound.computer}</strong><br><span style="font-size: 20px; margin-top: 10px; display: block;">${lastRound.result.toUpperCase()}</span>`;

            const trendsDiv = document.getElementById("trends");
            let trendText = "";
            if (lastRound.prediction) trendsDiv.innerHTML = "<em>AI was predicting: " + lastRound.prediction + "</em>";
        }

        function resetGame() {
            fetch("/api/reset", { method: "POST" }).then(() => location.reload());
        }
    </script>
</body>
</html>
    '''

    class GameHandler(http.server.BaseHTTPRequestHandler):
        ai = AdaptiveRPS()

        def do_GET(self):
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html_content.encode())
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            if self.path == "/api/play":
                import json
                content_length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(content_length).decode())
                move = body.get("move", "").lower()
                computer_move, result, status = self.ai.play_round(move)
                if status == "valid":
                    last_game = {
                        "player": move.capitalize(),
                        "computer": computer_move.capitalize(),
                        "result": result,
                        "prediction": self.ai.stats.predict_next_move()
                    }
                    wins, losses, ties, total, wp = self.ai.stats.get_winrate()
                    response = {
                        "games": [{"player": move, "computer": computer_move, "result": result, "prediction": self.ai.stats.predict_next_move()}],
                        "stats": {
                            "wins": wins,
                            "losses": losses,
                            "ties": ties,
                            "total": total,
                            "player_freq": dict(self.ai.stats.player_freq),
                            "pattern": self.ai.stats.detect_pattern(),
                        }
                    }
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    import json
                    self.wfile.write(json.dumps(response).encode())
            elif self.path == "/api/reset":
                self.ai = AdaptiveRPS()
                self.send_response(200)
                self.end_headers()

        def log_message(self, format, *args):
            pass  # Suppress logs

    try:
        with socketserver.TCPServer(("", port), GameHandler) as httpd:
            print(f"\n🎮 Web RPS server running at http://localhost:{port}")
            print("Opening browser...")
            webbrowser.open(f"http://localhost:{port}")
            print("Press Ctrl+C to stop.\n")
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {port} in use. Trying {port + 1}...")
            web_mode(port + 1)
        else:
            raise
    except KeyboardInterrupt:
        print("\nServer stopped.")


def main():
    parser = argparse.ArgumentParser(description="Adaptive Rock-Paper-Scissors AI")
    parser.add_argument("--cli", action="store_true", help="Play in CLI mode")
    parser.add_argument("--gui", action="store_true", help="Play in Tkinter GUI mode")
    parser.add_argument("--web", action="store_true", help="Play in web browser mode")
    parser.add_argument("--games", type=int, help="Number of games to play")
    args = parser.parse_args()

    if args.web:
        web_mode()
    elif args.gui:
        gui_mode()
    elif args.cli or args.games:
        cli_mode(args.games)
    else:
        # Default: try GUI, then web, then CLI
        try:
            gui_mode()
        except Exception:
            print("GUI mode failed (likely Tcl/Tk issue on macOS 1506).")
            print("Starting web mode instead...\n")
            try:
                web_mode()
            except Exception as e:
                print(f"Web mode failed: {e}")
                print("Falling back to CLI mode...\n")
                cli_mode()


if __name__ == "__main__":
    main()
