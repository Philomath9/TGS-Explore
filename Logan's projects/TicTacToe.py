"""Unbeatable Tic-Tac-Toe AI using Minimax Algorithm.

Play against an impossible-to-beat AI in your browser!

Features:
- Minimax algorithm ensures AI is unbeatable
- Beautiful responsive web interface
- Real-time game updates
- Game statistics

Usage:
  python3 TicTacToe.py          # Start web server (default)
  python3 TicTacToe.py --port 9000  # Use custom port
"""

import http.server
import socketserver
import json
import argparse
import webbrowser


class TicTacToeAI:
    """Unbeatable tic-tac-toe AI using minimax algorithm"""
    
    def __init__(self):
        self.HUMAN = -1
        self.AI = 1
        self.EMPTY = 0
    
    def check_winner(self, board):
        """Check if there's a winner. Returns AI (1), HUMAN (-1), or EMPTY (0)"""
        # Check rows
        for row in board:
            if row[0] == row[1] == row[2] != self.EMPTY:
                return row[0]
        
        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != self.EMPTY:
                return board[0][col]
        
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != self.EMPTY:
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != self.EMPTY:
            return board[0][2]
        
        return self.EMPTY
    
    def is_board_full(self, board):
        """Check if board is full"""
        for row in board:
            if self.EMPTY in row:
                return False
        return True
    
    def get_empty_cells(self, board):
        """Get list of empty cells as (row, col)"""
        empty = []
        for i in range(3):
            for j in range(3):
                if board[i][j] == self.EMPTY:
                    empty.append((i, j))
        return empty
    
    def minimax(self, board, depth, is_maximizing):
        """
        Minimax algorithm for optimal play
        is_maximizing: True when it's AI's turn, False when it's human's turn
        """
        winner = self.check_winner(board)
        
        # Terminal states
        if winner == self.AI:
            return 10 - depth  # Prefer faster wins
        if winner == self.HUMAN:
            return depth - 10  # Prefer slower losses
        if self.is_board_full(board):
            return 0  # Draw
        
        if is_maximizing:
            # AI's turn - maximize score
            max_eval = float('-inf')
            for row, col in self.get_empty_cells(board):
                board[row][col] = self.AI
                eval_score = self.minimax(board, depth + 1, False)
                board[row][col] = self.EMPTY
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            # Human's turn - minimize score
            min_eval = float('inf')
            for row, col in self.get_empty_cells(board):
                board[row][col] = self.HUMAN
                eval_score = self.minimax(board, depth + 1, True)
                board[row][col] = self.EMPTY
                min_eval = min(min_eval, eval_score)
            return min_eval
    
    def get_best_move(self, board):
        """Find the best move for the AI using minimax"""
        best_score = float('-inf')
        best_move = None
        
        for row, col in self.get_empty_cells(board):
            board[row][col] = self.AI
            score = self.minimax(board, 0, False)
            board[row][col] = self.EMPTY
            
            if score > best_score:
                best_score = score
                best_move = (row, col)
        
        return best_move
    
    def make_move(self, board, row, col, player):
        """Make a move on the board"""
        if board[row][col] == self.EMPTY:
            board[row][col] = player
            return True
        return False


HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unbeatable Tic-Tac-Toe AI</title>
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            text-align: center;
            max-width: 500px;
            width: 90%;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 32px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }

        .message {
            color: #667eea;
            font-weight: bold;
            margin-bottom: 20px;
            font-size: 16px;
            height: 24px;
        }

        .board {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-bottom: 30px;
            background: #f0f0f0;
            padding: 8px;
            border-radius: 10px;
        }

        .cell {
            width: 100%;
            aspect-ratio: 1;
            background: white;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 32px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s ease;
            color: #333;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .cell:hover:not(.disabled) {
            background: #f9f9f9;
            border-color: #667eea;
            transform: scale(1.05);
        }

        .cell.x {
            color: #667eea;
            font-weight: bold;
            cursor: not-allowed;
        }

        .cell.o {
            color: #764ba2;
            font-weight: bold;
            cursor: not-allowed;
        }

        .cell.disabled {
            cursor: not-allowed;
        }

        .buttons {
            display: flex;
            gap: 10px;
            justify-content: center;
        }

        button {
            padding: 12px 30px;
            font-size: 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: bold;
        }

        .btn-new {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            flex: 1;
            max-width: 200px;
        }

        .btn-new:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-new:active {
            transform: translateY(0);
        }

        .stats {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #f0f0f0;
            color: #666;
            font-size: 14px;
        }

        .winner-message {
            font-size: 18px;
            color: #764ba2;
            font-weight: bold;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ Tic-Tac-Toe AI</h1>
        <p class="subtitle">Can you beat the unbeatable AI?</p>
        
        <div class="message" id="message">Loading...</div>

        <div class="board" id="board">
            <!-- Cells generated by JavaScript -->
        </div>

        <div class="buttons">
            <button class="btn-new" onclick="resetGame()">New Game</button>
        </div>

        <div class="stats">
            <p>🟦 You are X (Blue) | 🟪 AI is O (Purple)</p>
            <p>The AI uses the Minimax algorithm - it's mathematically unbeatable!</p>
        </div>
    </div>

    <script>
        const HUMAN = -1;
        const AI = 1;
        const EMPTY = 0;

        let gameState = null;

        async function loadGame() {
            try {
                const response = await fetch('/api/game');
                gameState = await response.json();
                renderBoard();
                updateMessage();
            } catch (error) {
                console.error('Error loading game:', error);
                document.getElementById('message').textContent = 'Connection error';
            }
        }

        function renderBoard() {
            const boardDiv = document.getElementById('board');
            boardDiv.innerHTML = '';

            for (let row = 0; row < 3; row++) {
                for (let col = 0; col < 3; col++) {
                    const cell = document.createElement('button');
                    cell.className = 'cell';
                    
                    const value = gameState.board[row][col];
                    if (value === HUMAN) {
                        cell.textContent = 'X';
                        cell.classList.add('x', 'disabled');
                    } else if (value === AI) {
                        cell.textContent = 'O';
                        cell.classList.add('o', 'disabled');
                    } else {
                        cell.textContent = '';
                    }

                    if (!gameState.game_over && value === EMPTY) {
                        cell.onclick = () => makeMove(row, col);
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
                messageDiv.textContent = gameState.message;
            }
        }

        async function makeMove(row, col) {
            if (gameState.game_over) return;

            // Disable clicks during AI thinking
            document.getElementById('board').style.pointerEvents = 'none';
            document.getElementById('message').textContent = 'AI is thinking...';

            try {
                const response = await fetch('/api/move', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ row, col })
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

            document.getElementById('board').style.pointerEvents = 'auto';
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

        // Initialize game on page load
        loadGame();
    </script>
</body>
</html>
'''


class GameState:
    """Manages the game state"""
    def __init__(self):
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.game_over = False
        self.winner = None
        self.message = 'Your turn (X). You are X, AI is O.'
        self.ai = TicTacToeAI()
    
    def reset(self):
        """Reset the game"""
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.game_over = False
        self.winner = None
        self.message = 'Your turn (X). You are X, AI is O.'
    
    def to_dict(self):
        """Convert to dictionary for JSON"""
        return {
            'board': self.board,
            'game_over': self.game_over,
            'winner': self.winner,
            'message': self.message
        }


game_state = GameState()


class TicTacToeHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for tic-tac-toe server"""
    
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
            row, col = body.get('row'), body.get('col')
            
            if game_state.game_over:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Game is over'}).encode())
                return
            
            # Check if cell is empty
            if game_state.board[row][col] != 0:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Cell already occupied'}).encode())
                return
            
            # Make human move (represented as -1)
            game_state.board[row][col] = -1
            
            # Check if human won
            winner = game_state.ai.check_winner(game_state.board)
            if winner == -1:
                game_state.game_over = True
                game_state.winner = 'human'
                game_state.message = 'You won! (Surprise!)'
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
            move = game_state.ai.get_best_move(game_state.board)
            if move:
                game_state.board[move[0]][move[1]] = 1
            
            # Check if AI won
            winner = game_state.ai.check_winner(game_state.board)
            if winner == 1:
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
            
            game_state.message = 'Your turn'
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
    """Start the tic-tac-toe web server"""
    try:
        with socketserver.TCPServer(("", port), TicTacToeHandler) as httpd:
            print(f"\n🎮 Tic-Tac-Toe server running at http://localhost:{port}")
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
    parser = argparse.ArgumentParser(description="Unbeatable Tic-Tac-Toe AI")
    parser.add_argument("--port", type=int, default=8765, help="Port to run server on (default: 8765)")
    args = parser.parse_args()
    
    start_server(args.port)
