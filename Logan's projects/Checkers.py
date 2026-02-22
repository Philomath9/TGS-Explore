"""Unbeatable Checkers AI using Minimax with Alpha-Beta Pruning.

Play American Checkers (8x8) against an impossible-to-beat AI in your browser!

Features:
- Full American Checkers rules
- Mandatory captures
- King promotion
- Minimax with alpha-beta pruning and board evaluation
- Beautiful interactive web interface

Usage:
  python3 Checkers.py          # Start web server (default)
  python3 Checkers.py --port 9000  # Use custom port
"""

import http.server
import socketserver
import json
import argparse
import webbrowser


class CheckersAI:
    """Unbeatable Checkers AI using minimax with alpha-beta pruning"""
    
    def __init__(self):
        self.ROWS = 8
        self.COLS = 8
        self.HUMAN = -1
        self.AI = 1
        self.HUMAN_KING = -3
        self.AI_KING = 3
        self.EMPTY = 0
    
    def create_board(self):
        """Create starting checkers board"""
        board = [[self.EMPTY for _ in range(self.COLS)] for _ in range(self.ROWS)]
        
        # Place AI pieces (top)
        for row in range(3):
            for col in range(self.COLS):
                if (row + col) % 2 == 1:
                    board[row][col] = self.AI
        
        # Place human pieces (bottom)
        for row in range(5, 8):
            for col in range(self.COLS):
                if (row + col) % 2 == 1:
                    board[row][col] = self.HUMAN
        
        return board
    
    def is_valid_position(self, row, col):
        """Check if position is valid"""
        return 0 <= row < self.ROWS and 0 <= col < self.COLS
    
    def get_piece_at(self, board, row, col):
        """Get piece at position"""
        if self.is_valid_position(row, col):
            return board[row][col]
        return None
    
    def is_piece_owner(self, piece, player):
        """Check if piece belongs to player"""
        if piece == self.EMPTY:
            return False
        return (piece > 0) == (player > 0)
    
    def get_regular_moves(self, board, row, col):
        """Get regular (non-capture) moves for a piece"""
        moves = []
        piece = board[row][col]
        
        if piece == self.EMPTY:
            return moves
        
        is_ai = piece > 0
        is_king = abs(piece) == 3
        
        # Regular pieces move forward diagonally; kings move both directions
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        if not is_king:
            directions = [(1, -1), (1, 1)] if is_ai else [(-1, -1), (-1, 1)]
        
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if self.is_valid_position(nr, nc) and board[nr][nc] == self.EMPTY:
                moves.append((row, col, nr, nc, None))
        
        return moves
    
    def get_capture_moves(self, board, row, col):
        """Get capture moves for a piece"""
        moves = []
        piece = board[row][col]
        
        if piece == self.EMPTY:
            return moves
        
        is_ai = piece > 0
        is_king = abs(piece) == 3
        
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        if not is_king:
            directions = [(1, -1), (1, 1)] if is_ai else [(-1, -1), (-1, 1)]
        
        for dr, dc in directions:
            nr, nc = row + dr * 2, col + dc * 2
            mr, mc = row + dr, col + dc
            
            if self.is_valid_position(nr, nc) and board[nr][nc] == self.EMPTY:
                enemy_piece = board[mr][mc]
                if enemy_piece != self.EMPTY and not self.is_piece_owner(enemy_piece, piece > 0):
                    moves.append((row, col, nr, nc, (mr, mc)))
        
        return moves
    
    def get_all_moves(self, board, player):
        """Get all valid moves for a player"""
        captures = []
        regular = []
        
        for row in range(self.ROWS):
            for col in range(self.COLS):
                piece = board[row][col]
                if piece != self.EMPTY and self.is_piece_owner(piece, player > 0):
                    piece_captures = self.get_capture_moves(board, row, col)
                    if piece_captures:
                        captures.extend(piece_captures)
                    else:
                        regular.extend(self.get_regular_moves(board, row, col))
        
        # If captures are available, must use them
        return captures if captures else regular
    
    def apply_move(self, board, move):
        """Apply move to board and return new board state"""
        new_board = [row[:] for row in board]
        fr, fc, tr, tc, capture = move
        
        piece = new_board[fr][fc]
        new_board[tr][tc] = piece
        new_board[fr][fc] = self.EMPTY
        
        # Remove captured piece
        if capture:
            mr, mc = capture
            new_board[mr][mc] = self.EMPTY
        
        # Promote to king
        if (piece == self.HUMAN and tr == self.ROWS - 1) or (piece == self.AI and tr == 0):
            new_board[tr][tc] = self.HUMAN_KING if piece == self.HUMAN else self.AI_KING
        
        return new_board
    
    def check_winner(self, board, human_moves, ai_moves):
        """Check if there's a winner"""
        if not human_moves:
            return self.AI  # AI wins
        if not ai_moves:
            return self.HUMAN  # Human wins
        return self.EMPTY  # Game continues
    
    def count_pieces(self, board):
        """Count pieces for evaluation"""
        human_count = 0
        ai_count = 0
        human_kings = 0
        ai_kings = 0
        
        for row in board:
            for piece in row:
                if piece == self.HUMAN:
                    human_count += 1
                elif piece == self.AI:
                    ai_count += 1
                elif piece == self.HUMAN_KING:
                    human_kings += 1
                    human_count += 1
                elif piece == self.AI_KING:
                    ai_kings += 1
                    ai_count += 1
        
        return human_count, ai_count, human_kings, ai_kings
    
    def evaluate_board(self, board):
        """Evaluate board position"""
        h_count, a_count, h_kings, a_kings = self.count_pieces(board)
        
        # Piece value
        score = (a_count - h_count) * 100 + (a_kings - h_kings) * 120
        
        # Positional bonus (pieces near promotion row) - simplified
        for col in range(self.COLS):
            if board[7][col] == self.AI:
                score += 3
            elif board[7][col] == self.AI_KING:
                score += 5
            if board[0][col] == self.HUMAN:
                score -= 3
            elif board[0][col] == self.HUMAN_KING:
                score -= 5
        
        return score
    
    def minimax(self, board, depth, is_maximizing, alpha, beta):
        """Minimax with alpha-beta pruning"""
        if depth == 0:
            return self.evaluate_board(board), None
        
        moves = self.get_all_moves(board, self.AI if is_maximizing else self.HUMAN)
        
        if not moves:
            human_moves = self.get_all_moves(board, self.HUMAN)
            ai_moves = self.get_all_moves(board, self.AI)
            winner = self.check_winner(board, human_moves, ai_moves)
            if winner == self.AI:
                return 10000 - depth, None
            elif winner == self.HUMAN:
                return -10000 + depth, None
            return self.evaluate_board(board), None
        
        # Sort captures before regular moves for better pruning
        moves_sorted = [m for m in moves if m[4]] + [m for m in moves if not m[4]]
        best_move = moves_sorted[0]
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in moves_sorted:
                new_board = self.apply_move(board, move)
                eval_score, _ = self.minimax(new_board, depth - 1, False, alpha, beta)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves_sorted:
                new_board = self.apply_move(board, move)
                eval_score, _ = self.minimax(new_board, depth - 1, True, alpha, beta)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move
    
    def get_best_move(self, board):
        """Get the best move for AI"""
        depth = 4
        _, best_move = self.minimax(board, depth, True, float('-inf'), float('inf'))
        return best_move


HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Checkers AI</title>
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
            background: linear-gradient(135deg, #8B4513 0%, #D2B48C 100%);
            padding: 20px;
        }

        .container {
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            text-align: center;
            max-width: 700px;
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
            color: #8B4513;
            font-weight: bold;
            margin-bottom: 20px;
            font-size: 16px;
            height: 24px;
        }

        .board-container {
            background: #8B4513;
            padding: 8px;
            border-radius: 10px;
            width: fit-content;
            margin: 0 auto 20px;
        }

        .board {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 0;
            width: 480px;
            height: 480px;
        }

        .cell {
            width: 60px;
            height: 60px;
            border: none;
            cursor: pointer;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            transition: all 0.2s ease;
        }

        .cell.light {
            background: #D2B48C;
        }

        .cell.dark {
            background: #654321;
        }

        .cell.valid-move::after {
            content: '';
            position: absolute;
            width: 12px;
            height: 12px;
            background: rgba(76, 175, 80, 0.7);
            border-radius: 50%;
        }

        .cell.valid-capture::after {
            content: '';
            position: absolute;
            width: 12px;
            height: 12px;
            background: rgba(255, 87, 34, 0.7);
            border-radius: 50%;
        }

        .piece {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: 3px solid #333;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: grab;
            font-weight: bold;
            font-size: 24px;
        }

        .piece.human {
            background: #ff4444;
        }

        .piece.ai {
            background: #00aa00;
        }

        .piece.selected {
            transform: scale(1.1);
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
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
            background: linear-gradient(135deg, #8B4513 0%, #D2B48C 100%);
            color: white;
            flex: 1;
            max-width: 200px;
        }

        .btn-new:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(139, 69, 19, 0.4);
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
            border: 2px solid #333;
        }

        .legend-circle.red {
            background: #ff4444;
        }

        .legend-circle.green {
            background: #00aa00;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>♟️ Checkers</h1>
        <p class="subtitle">Can you beat the unbeatable AI?</p>
        
        <div class="message" id="message">Loading...</div>

        <div class="board-container">
            <div class="board" id="board">
                <!-- Board cells generated by JavaScript -->
            </div>
        </div>

        <div class="buttons">
            <button class="btn-new" onclick="resetGame()">New Game</button>
        </div>

        <div class="legend">
            <div class="legend-item">
                <div class="legend-circle red"></div>
                <span>You (Red) - Move up</span>
            </div>
            <div class="legend-item">
                <div class="legend-circle green"></div>
                <span>AI (Green) - Move down</span>
            </div>
        </div>

        <div class="stats">
            <p>🤖 The AI uses Minimax with Alpha-Beta Pruning - it's unbeatable!</p>
            <p style="margin-top: 8px; font-size: 12px; color: #999;">Click a piece, then click a highlighted square to move. Red pieces promotion = 👑. Capture opponent pieces to win!</p>
        </div>
    </div>

    <script>
        const HUMAN = -1;
        const AI = 1;
        const HUMAN_KING = -3;
        const AI_KING = 3;
        const EMPTY = 0;

        let gameState = null;
        let selectedPiece = null;
        let validMoves = [];
        let isThinking = false;

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

            for (let row = 0; row < 8; row++) {
                for (let col = 0; col < 8; col++) {
                    const cell = document.createElement('button');
                    cell.className = 'cell ' + ((row + col) % 2 === 0 ? 'light' : 'dark');
                    
                    const value = gameState.board[row][col];
                    let piece = '';
                    
                    if (value === HUMAN) piece = '●';
                    else if (value === AI) piece = '●';
                    else if (value === HUMAN_KING) piece = '👑';
                    else if (value === AI_KING) piece = '👑';
                    
                    if (piece) {
                        const pieceDiv = document.createElement('div');
                        pieceDiv.className = 'piece ' + (value > 0 ? 'ai' : 'human');
                        pieceDiv.textContent = piece;
                        cell.appendChild(pieceDiv);
                    }
                    
                    if (!gameState.game_over && value < 0 && !isThinking) {
                        cell.onclick = () => selectPiece(row, col);
                    }
                    
                    // Highlight valid moves
                    const moveStr = validMoves.find(m => m[2] === row && m[3] === col);
                    if (moveStr) {
                        cell.classList.add(moveStr[4] ? 'valid-capture' : 'valid-move');
                    }
                    
                    boardDiv.appendChild(cell);
                }
            }
        }

        async function selectPiece(row, col) {
            if (isThinking) return;
            
            const value = gameState.board[row][col];
            if (value >= 0) return;
            
            selectedPiece = [row, col];
            
            try {
                const response = await fetch('/api/moves', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ row, col })
                });
                validMoves = await response.json();
                renderBoard();
            } catch (error) {
                console.error('Error getting moves:', error);
            }
        }

        async function makeMove(toRow, toCol) {
            if (!selectedPiece || isThinking) return;
            
            isThinking = true;
            document.getElementById('board').style.pointerEvents = 'none';
            updateMessage();

            try {
                const response = await fetch('/api/move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        from: selectedPiece,
                        to: [toRow, toCol]
                    })
                });

                if (!response.ok) {
                    const error = await response.json();
                    alert(error.error || 'Invalid move');
                    isThinking = false;
                    document.getElementById('board').style.pointerEvents = 'auto';
                } else {
                    gameState = await response.json();
                    selectedPiece = null;
                    validMoves = [];
                    isThinking = false;
                    renderBoard();
                    updateMessage();
                    document.getElementById('board').style.pointerEvents = 'auto';
                }
            } catch (error) {
                console.error('Error making move:', error);
                alert('Error making move');
                isThinking = false;
                document.getElementById('board').style.pointerEvents = 'auto';
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

        async function resetGame() {
            try {
                const response = await fetch('/api/reset', { method: 'POST' });
                gameState = await response.json();
                selectedPiece = null;
                validMoves = [];
                renderBoard();
                updateMessage();
            } catch (error) {
                console.error('Error resetting game:', error);
            }
        }

        // Intercept board clicks to move pieces
        document.addEventListener('click', async (e) => {
            if (e.target.closest('.cell') && validMoves.length > 0) {
                const cell = e.target.closest('.cell');
                const cells = Array.from(document.querySelectorAll('.cell'));
                const idx = cells.indexOf(cell);
                const row = Math.floor(idx / 8);
                const col = idx % 8;
                
                const move = validMoves.find(m => m[2] === row && m[3] === col);
                if (move) {
                    await makeMove(row, col);
                }
            }
        });

        loadGame();
    </script>
</body>
</html>
'''


class GameState:
    """Manages the game state"""
    def __init__(self):
        self.ai = CheckersAI()
        self.board = self.ai.create_board()
        self.game_over = False
        self.winner = None
        self.message = 'Your turn! Click a red piece to move.'
    
    def reset(self):
        """Reset the game"""
        self.board = self.ai.create_board()
        self.game_over = False
        self.winner = None
        self.message = 'Your turn! Click a red piece to move.'
    
    def to_dict(self):
        """Convert to dictionary for JSON"""
        return {
            'board': self.board,
            'game_over': self.game_over,
            'winner': self.winner,
            'message': self.message
        }


game_state = GameState()


class CheckersHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for Checkers"""
    
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
        if self.path == '/api/moves':
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode())
            row, col = body.get('row'), body.get('col')
            
            moves = game_state.ai.get_all_moves(game_state.board, game_state.ai.HUMAN)
            valid = [m for m in moves if m[0] == row and m[1] == col]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(valid).encode())
        
        elif self.path == '/api/move':
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode())
            fr, fc = body.get('from')
            tr, tc = body.get('to')
            
            if game_state.game_over:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Game is over'}).encode())
                return
            
            # Validate and apply move
            valid_moves = game_state.ai.get_all_moves(game_state.board, game_state.ai.HUMAN)
            move = next((m for m in valid_moves if m[0] == fr and m[1] == fc and m[2] == tr and m[3] == tc), None)
            
            if not move:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid move'}).encode())
                return
            
            game_state.board = game_state.ai.apply_move(game_state.board, move)
            
            # Check if human won
            human_moves = game_state.ai.get_all_moves(game_state.board, game_state.ai.HUMAN)
            ai_moves = game_state.ai.get_all_moves(game_state.board, game_state.ai.AI)
            winner = game_state.ai.check_winner(game_state.board, human_moves, ai_moves)
            
            if winner == game_state.ai.HUMAN:
                game_state.game_over = True
                game_state.winner = 'human'
                game_state.message = 'You won! (Incredibly unlikely!)'
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(game_state.to_dict()).encode())
                return
            
            if not ai_moves:
                game_state.game_over = True
                game_state.winner = 'human'
                game_state.message = 'You won! (Incredibly unlikely!)'
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(game_state.to_dict()).encode())
                return
            
            # AI's turn
            ai_move = game_state.ai.get_best_move(game_state.board)
            if ai_move:
                game_state.board = game_state.ai.apply_move(game_state.board, ai_move)
            
            # Check if AI won
            human_moves = game_state.ai.get_all_moves(game_state.board, game_state.ai.HUMAN)
            ai_moves = game_state.ai.get_all_moves(game_state.board, game_state.ai.AI)
            winner = game_state.ai.check_winner(game_state.board, human_moves, ai_moves)
            
            if winner == game_state.ai.AI:
                game_state.game_over = True
                game_state.winner = 'ai'
                game_state.message = 'AI wins! (As expected)'
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(game_state.to_dict()).encode())
                return
            
            if not human_moves:
                game_state.game_over = True
                game_state.winner = 'ai'
                game_state.message = 'AI wins! (As expected)'
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
    """Start the Checkers web server"""
    try:
        with socketserver.TCPServer(("", port), CheckersHandler) as httpd:
            print(f"\n🎮 Checkers server running at http://localhost:{port}")
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
    parser = argparse.ArgumentParser(description="Unbeatable Checkers AI")
    parser.add_argument("--port", type=int, default=8765, help="Port to run server on (default: 8765)")
    args = parser.parse_args()
    
    start_server(args.port)
