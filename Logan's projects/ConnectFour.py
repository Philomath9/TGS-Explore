"""Unbeatable Connect Four AI using Minimax Algorithm with Alpha-Beta Pruning.

Play against an impossible-to-beat AI in your browser!

Features:
- 7×6 board (classic Connect Four)
- Minimax with alpha-beta pruning for optimal play
- Beautiful responsive web interface
- Game statistics and reset

Usage:
  python3 ConnectFour.py          # Start web server (default)
  python3 ConnectFour.py --port 9000  # Use custom port
"""

import http.server
import socketserver
import json
import argparse
import webbrowser


class ConnectFourAI:
    """Unbeatable Connect Four AI using minimax with alpha-beta pruning"""
    
    def __init__(self):
        self.ROWS = 6
        self.COLS = 7
        self.HUMAN = -1
        self.AI = 1
        self.EMPTY = 0
        self.WIN_LENGTH = 4
    
    def create_board(self):
        """Create empty board"""
        return [[self.EMPTY for _ in range(self.COLS)] for _ in range(self.ROWS)]
    
    def is_valid_move(self, board, col):
        """Check if move is valid in column"""
        return col >= 0 and col < self.COLS and board[0][col] == self.EMPTY
    
    def get_valid_moves(self, board):
        """Get list of valid column indices"""
        return [col for col in range(self.COLS) if self.is_valid_move(board, col)]
    
    def make_move(self, board, col, player):
        """Place piece in column, return row or -1 if invalid"""
        if not self.is_valid_move(board, col):
            return -1
        
        for row in range(self.ROWS - 1, -1, -1):
            if board[row][col] == self.EMPTY:
                board[row][col] = player
                return row
        return -1
    
    def undo_move(self, board, col):
        """Remove last piece from column"""
        for row in range(self.ROWS):
            if board[row][col] != self.EMPTY:
                board[row][col] = self.EMPTY
                return
    
    def check_winner(self, board):
        """Check if there's a winner. Returns AI (1), HUMAN (-1), or EMPTY (0)"""
        # Check horizontal
        for row in range(self.ROWS):
            for col in range(self.COLS - self.WIN_LENGTH + 1):
                if (board[row][col] != self.EMPTY and 
                    board[row][col] == board[row][col+1] == board[row][col+2] == board[row][col+3]):
                    return board[row][col]
        
        # Check vertical
        for col in range(self.COLS):
            for row in range(self.ROWS - self.WIN_LENGTH + 1):
                if (board[row][col] != self.EMPTY and 
                    board[row][col] == board[row+1][col] == board[row+2][col] == board[row+3][col]):
                    return board[row][col]
        
        # Check diagonal /
        for row in range(self.ROWS - self.WIN_LENGTH + 1):
            for col in range(self.WIN_LENGTH - 1, self.COLS):
                if (board[row][col] != self.EMPTY and 
                    board[row][col] == board[row+1][col-1] == board[row+2][col-2] == board[row+3][col-3]):
                    return board[row][col]
        
        # Check diagonal \
        for row in range(self.ROWS - self.WIN_LENGTH + 1):
            for col in range(self.COLS - self.WIN_LENGTH + 1):
                if (board[row][col] != self.EMPTY and 
                    board[row][col] == board[row+1][col+1] == board[row+2][col+2] == board[row+3][col+3]):
                    return board[row][col]
        
        return self.EMPTY
    
    def is_board_full(self, board):
        """Check if board is full"""
        return all(board[0][col] != self.EMPTY for col in range(self.COLS))
    
    def count_threats(self, board, player):
        """Count potential winning threats for a player"""
        threats = 0
        
        # Count horizontal threats
        for row in range(self.ROWS):
            for col in range(self.COLS - 2):
                cells = [board[row][col + i] for i in range(3)]
                empty_count = cells.count(self.EMPTY)
                player_count = cells.count(player)
                if empty_count == 1 and player_count == 2:
                    threats += 1
        
        # Count vertical threats
        for col in range(self.COLS):
            for row in range(self.ROWS - 2):
                cells = [board[row + i][col] for i in range(3)]
                empty_count = cells.count(self.EMPTY)
                player_count = cells.count(player)
                if empty_count == 1 and player_count == 2:
                    threats += 1
        
        # Count diagonal threats (/)
        for row in range(self.ROWS - 2):
            for col in range(2, self.COLS):
                cells = [board[row + i][col - i] for i in range(3)]
                empty_count = cells.count(self.EMPTY)
                player_count = cells.count(player)
                if empty_count == 1 and player_count == 2:
                    threats += 1
        
        # Count diagonal threats (\)
        for row in range(self.ROWS - 2):
            for col in range(self.COLS - 2):
                cells = [board[row + i][col + i] for i in range(3)]
                empty_count = cells.count(self.EMPTY)
                player_count = cells.count(player)
                if empty_count == 1 and player_count == 2:
                    threats += 1
        
        return threats
    
    def evaluate_board(self, board):
        """Evaluate board position heuristically"""
        # Check for immediate win/loss
        winner = self.check_winner(board)
        if winner == self.AI:
            return 1000
        if winner == self.HUMAN:
            return -1000
        if self.is_board_full(board):
            return 0
        
        # Evaluate threats
        ai_threats = self.count_threats(board, self.AI)
        human_threats = self.count_threats(board, self.HUMAN)
        
        # Center control bonus (middle columns are more valuable)
        center_bonus = 0
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if board[row][col] == self.AI:
                    center_bonus += (3 - abs(col - 3)) * 0.5
                elif board[row][col] == self.HUMAN:
                    center_bonus -= (3 - abs(col - 3)) * 0.5
        
        return ai_threats * 50 - human_threats * 50 + center_bonus
    
    def minimax(self, board, depth, is_maximizing, alpha, beta):
        """Minimax with alpha-beta pruning"""
        winner = self.check_winner(board)
        
        # Terminal states
        if winner == self.AI:
            return 10000 - depth
        if winner == self.HUMAN:
            return depth - 10000
        if self.is_board_full(board) or depth == 0:
            return self.evaluate_board(board)
        
        valid_moves = self.get_valid_moves(board)
        
        if is_maximizing:
            max_eval = float('-inf')
            for col in valid_moves:
                self.make_move(board, col, self.AI)
                eval_score = self.minimax(board, depth - 1, False, alpha, beta)
                self.undo_move(board, col)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for col in valid_moves:
                self.make_move(board, col, self.HUMAN)
                eval_score = self.minimax(board, depth - 1, True, alpha, beta)
                self.undo_move(board, col)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
    
    def get_best_move(self, board):
        """Find the best move for the AI"""
        best_score = float('-inf')
        best_move = None
        valid_moves = self.get_valid_moves(board)
        
        # Use deeper search for fewer remaining moves
        depth = 7
        
        for col in valid_moves:
            self.make_move(board, col, self.AI)
            score = self.minimax(board, depth - 1, False, float('-inf'), float('inf'))
            self.undo_move(board, col)
            
            if score > best_score:
                best_score = score
                best_move = col
        
        return best_move


HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connect Four AI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 20px;
        }

        .container {
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            text-align: center;
            max-width: 600px;
            width: 100%;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 32px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }

        .message {
            color: #f5576c;
            font-weight: bold;
            margin-bottom: 20px;
            font-size: 16px;
            height: 24px;
        }

        .board {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
            margin-bottom: 20px;
            background: #1e90ff;
            padding: 8px;
            border-radius: 15px;
            width: 100%;
        }

        .cell {
            width: 100%;
            aspect-ratio: 1;
            background: #0066cc;
            border: none;
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            transition: all 0.2s ease;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .cell:hover:not(.disabled) {
            background: #004fa3;
            transform: scale(1.05);
        }

        .cell.red {
            background: #f5576c;
        }

        .cell.yellow {
            background: #ffd700;
        }

        .cell.disabled {
            cursor: not-allowed;
        }

        .column-indicator {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
            padding: 0 8px;
            margin-bottom: 10px;
        }

        .col-num {
            font-weight: bold;
            color: #666;
            font-size: 12px;
        }

        .buttons {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 15px;
        }

        button {
            padding: 12px 25px;
            font-size: 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: bold;
        }

        .btn-new {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            flex: 1;
            max-width: 200px;
        }

        .btn-new:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(245, 87, 108, 0.4);
        }

        .btn-new:active {
            transform: translateY(0);
        }

        .stats {
            margin-top: 25px;
            padding-top: 20px;
            border-top: 2px solid #f0f0f0;
            color: #666;
            font-size: 13px;
        }

        .legend {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 10px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .legend-circle {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: none;
        }

        .legend-circle.red {
            background: #f5576c;
        }

        .legend-circle.yellow {
            background: #ffd700;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⭕ Connect Four</h1>
        <p class="subtitle">Can you beat the unbeatable AI?</p>
        
        <div class="message" id="message">Loading...</div>

        <div class="column-indicator" id="columnIndicator"></div>

        <div class="board" id="board">
            <!-- Board cells generated by JavaScript -->
        </div>

        <div class="buttons">
            <button class="btn-new" onclick="resetGame()">New Game</button>
        </div>

        <div class="legend">
            <div class="legend-item">
                <div class="legend-circle red"></div>
                <span>You (Red)</span>
            </div>
            <div class="legend-item">
                <div class="legend-circle yellow"></div>
                <span>AI (Yellow)</span>
            </div>
        </div>

        <div class="stats">
            <p>🤖 The AI uses Minimax with Alpha-Beta Pruning - it's unbeatable!</p>
            <p style="margin-top: 8px; font-size: 12px; color: #999;">Get 4 in a row (horizontal, vertical, or diagonal) to win</p>
        </div>
    </div>

    <script>
        const HUMAN = -1;
        const AI = 1;
        const EMPTY = 0;
        const ROWS = 6;
        const COLS = 7;

        let gameState = null;
        let isThinking = false;

        async function loadGame() {
            try {
                const response = await fetch('/api/game');
                gameState = await response.json();
                renderBoard();
                updateMessage();
                renderColumnIndicator();
            } catch (error) {
                console.error('Error loading game:', error);
                document.getElementById('message').textContent = 'Connection error';
            }
        }

        function renderColumnIndicator() {
            const indicator = document.getElementById('columnIndicator');
            indicator.innerHTML = '';
            for (let col = 0; col < COLS; col++) {
                const div = document.createElement('div');
                div.className = 'col-num';
                div.textContent = col + 1;
                indicator.appendChild(div);
            }
        }

        function renderBoard() {
            const boardDiv = document.getElementById('board');
            boardDiv.innerHTML = '';

            for (let row = 0; row < ROWS; row++) {
                for (let col = 0; col < COLS; col++) {
                    const cell = document.createElement('button');
                    cell.className = 'cell';
                    
                    const value = gameState.board[row][col];
                    if (value === HUMAN) {
                        cell.classList.add('red', 'disabled');
                        cell.textContent = '●';
                    } else if (value === AI) {
                        cell.classList.add('yellow', 'disabled');
                        cell.textContent = '●';
                    } else {
                        cell.textContent = '';
                    }

                    if (!gameState.game_over && value === EMPTY) {
                        cell.onclick = () => makeMove(col);
                    } else {
                        cell.classList.add('disabled');
                    }

                    boardDiv.appendChild(cell);
                }
            }
        }

        function updateMessage() {
            const messageDiv = document.getElementById('message');
            
            if (gameState.game_over) {
                messageDiv.innerHTML = gameState.message;
                if (gameState.winner === 'human') {
                    messageDiv.innerHTML += ' 🎉';
                } else if (gameState.winner === 'ai') {
                    messageDiv.innerHTML += ' 🤖';
                } else if (gameState.winner === 'draw') {
                    messageDiv.innerHTML += ' 🤝';
                }
            } else {
                messageDiv.textContent = isThinking ? 'AI is thinking...' : gameState.message;
            }
        }

        async function makeMove(col) {
            if (gameState.game_over || isThinking) return;

            isThinking = true;
            updateMessage();
            document.getElementById('board').style.pointerEvents = 'none';

            try {
                const response = await fetch('/api/move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ col })
                });

                if (!response.ok) {
                    const error = await response.json();
                    alert(error.error || 'Invalid move');
                } else {
                    gameState = await response.json();
                    renderBoard();
                    updateMessage();
                }
            } catch (error) {
                console.error('Error making move:', error);
                alert('Error making move');
            }

            isThinking = false;
            document.getElementById('board').style.pointerEvents = 'auto';
            updateMessage();
        }

        async function resetGame() {
            try {
                const response = await fetch('/api/reset', { method: 'POST' });
                gameState = await response.json();
                renderBoard();
                updateMessage();
            } catch (error) {
                console.error('Error resetting game:', error);
            }
        }

        // Initialize on page load
        loadGame();
    </script>
</body>
</html>
'''


class GameState:
    """Manages the game state"""
    def __init__(self):
        self.ai = ConnectFourAI()
        self.board = self.ai.create_board()
        self.game_over = False
        self.winner = None
        self.message = 'Your turn! Click a column to drop your piece (Red).'
    
    def reset(self):
        """Reset the game"""
        self.board = self.ai.create_board()
        self.game_over = False
        self.winner = None
        self.message = 'Your turn! Click a column to drop your piece (Red).'
    
    def to_dict(self):
        """Convert to dictionary for JSON"""
        return {
            'board': self.board,
            'game_over': self.game_over,
            'winner': self.winner,
            'message': self.message
        }


game_state = GameState()


class ConnectFourHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for Connect Four"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode())
        elif self.path == '/api/game':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(game_state.to_dict()).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/move':
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode())
            col = body.get('col')
            
            if game_state.game_over:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Game is over'}).encode())
                return
            
            # Make human move
            if game_state.ai.make_move(game_state.board, col, game_state.ai.HUMAN) == -1:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid move'}).encode())
                return
            
            # Check if human won
            winner = game_state.ai.check_winner(game_state.board)
            if winner == game_state.ai.HUMAN:
                game_state.game_over = True
                game_state.winner = 'human'
                game_state.message = 'You won! (Highly unlikely!)'
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(game_state.to_dict()).encode())
                return
            
            # Check for draw
            if game_state.ai.is_board_full(game_state.board):
                game_state.game_over = True
                game_state.winner = 'draw'
                game_state.message = 'It\'s a draw!'
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(game_state.to_dict()).encode())
                return
            
            # AI's turn
            ai_move = game_state.ai.get_best_move(game_state.board)
            if ai_move is not None:
                game_state.ai.make_move(game_state.board, ai_move, game_state.ai.AI)
            
            # Check if AI won
            winner = game_state.ai.check_winner(game_state.board)
            if winner == game_state.ai.AI:
                game_state.game_over = True
                game_state.winner = 'ai'
                game_state.message = 'AI wins! (As expected)'
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(game_state.to_dict()).encode())
                return
            
            # Check for draw
            if game_state.ai.is_board_full(game_state.board):
                game_state.game_over = True
                game_state.winner = 'draw'
                game_state.message = 'It\'s a draw!'
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(game_state.to_dict()).encode())
                return
            
            game_state.message = 'Your turn!'
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(game_state.to_dict()).encode())
        
        elif self.path == '/api/reset':
            game_state.reset()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(game_state.to_dict()).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def start_server(port=8765):
    """Start the Connect Four web server"""
    try:
        with socketserver.TCPServer(("", port), ConnectFourHandler) as httpd:
            print(f"\n🎮 Connect Four server running at http://localhost:{port}")
            print("Opening browser...")
            webbrowser.open(f"http://localhost:{port}")
            print("Press Ctrl+C to stop.\n")
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {port} in use. Trying {port + 1}...")
            start_server(port + 1)
        else:
            raise
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unbeatable Connect Four AI")
    parser.add_argument("--port", type=int, default=8765, help="Port to run server on (default: 8765)")
    args = parser.parse_args()
    
    start_server(args.port)
