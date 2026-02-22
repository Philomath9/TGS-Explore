"""AI Snake Game - Compete against an intelligent AI snake

Features:
- Classic Snake gameplay
- Competitive AI opponent
- Real-time multiplayer on shared board
- Beautiful web interface
- AI uses pathfinding to hunt food and avoid obstacles

Usage:
  python3 Snake.py          # Start web server (default)
  python3 Snake.py --port 9000  # Use custom port
"""

import http.server
import socketserver
import json
import argparse
import webbrowser
import random
from collections import deque


class SnakeGame:
    """Manages the snake game state and AI logic"""
    
    BOARD_SIZE = 20
    FOOD_SCORE = 10
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Initialize game state"""
        # Player snake (controlled by user) - starts on left
        self.player_snake = [(2, self.BOARD_SIZE // 2)]
        self.player_direction = (1, 0)
        self.player_next_direction = (1, 0)
        self.player_score = 0
        self.player_alive = True
        
        # AI snake - starts on right
        self.ai_snake = [(self.BOARD_SIZE - 3, self.BOARD_SIZE // 2)]
        self.ai_direction = (-1, 0)
        self.ai_score = 0
        self.ai_alive = True
        
        # Food
        self.food = self.spawn_food()
        
        # Game state
        self.tick = 0
        self.game_over = False
        self.winner = None
    
    def spawn_food(self):
        """Spawn food at random location not occupied by snakes"""
        while True:
            food = (random.randint(0, self.BOARD_SIZE - 1), 
                   random.randint(0, self.BOARD_SIZE - 1))
            if food not in self.player_snake and food not in self.ai_snake:
                return food
    
    def get_occupied_cells(self):
        """Get all occupied cells on board"""
        occupied = set(self.player_snake + self.ai_snake)
        return occupied
    
    def ai_find_path_to_food(self):
        """Use BFS to find shortest path to food"""
        head = self.ai_snake[0]
        target = self.food
        
        queue = deque([(head, [])])
        visited = {head}
        occupied = self.get_occupied_cells()
        
        while queue:
            (x, y), path = queue.popleft()
            
            if (x, y) == target:
                if path:
                    return path[0]
                return self.ai_direction
            
            # Try all 4 directions
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                
                # Check bounds
                if 0 <= nx < self.BOARD_SIZE and 0 <= ny < self.BOARD_SIZE:
                    # Check if not occupied (or is the food)
                    if (nx, ny) not in visited and (nx, ny) not in occupied:
                        visited.add((nx, ny))
                        new_path = path + [(dx, dy)]
                        queue.append(((nx, ny), new_path))
        
        # No path found, try to avoid walls and find open space
        return self.ai_find_safe_direction()
    
    def ai_find_safe_direction(self):
        """Find a safe direction to move (avoid walls and body)"""
        head = self.ai_snake[0]
        occupied = self.get_occupied_cells()
        occupied.discard(head)  # Don't count head as occupied
        
        safe_dirs = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = head[0] + dx, head[1] + dy
            
            # Check bounds
            if 0 <= nx < self.BOARD_SIZE and 0 <= ny < self.BOARD_SIZE:
                # Check if not occupied
                if (nx, ny) not in occupied:
                    safe_dirs.append((dx, dy))
        
        if safe_dirs:
            return random.choice(safe_dirs)
        return self.ai_direction
    
    def update(self, player_direction=None):
        """Update game state for one tick"""
        if self.game_over:
            return
        
        # Update player direction if provided
        if player_direction:
            # Prevent reversing into self
            if (player_direction[0] * -1, player_direction[1] * -1) != self.player_direction:
                self.player_next_direction = player_direction
        
        # Move player snake
        if self.player_alive:
            self.player_direction = self.player_next_direction
            head = self.player_snake[0]
            new_head = (head[0] + self.player_direction[0], 
                       head[1] + self.player_direction[1])
            
            # Check collisions
            if (new_head[0] < 0 or new_head[0] >= self.BOARD_SIZE or 
                new_head[1] < 0 or new_head[1] >= self.BOARD_SIZE or
                new_head in self.player_snake):
                self.player_alive = False
            else:
                self.player_snake.insert(0, new_head)
                
                # Check if ate food
                if new_head == self.food:
                    self.player_score += self.FOOD_SCORE
                    self.food = self.spawn_food()
                else:
                    self.player_snake.pop()
                
                # Check if hit AI snake
                if new_head in self.ai_snake:
                    self.player_alive = False
        
        # Move AI snake
        if self.ai_alive:
            ai_direction = self.ai_find_path_to_food()
            self.ai_direction = ai_direction
            head = self.ai_snake[0]
            new_head = (head[0] + self.ai_direction[0], 
                       head[1] + self.ai_direction[1])
            
            # Check collisions
            if (new_head[0] < 0 or new_head[0] >= self.BOARD_SIZE or 
                new_head[1] < 0 or new_head[1] >= self.BOARD_SIZE or
                new_head in self.ai_snake):
                self.ai_alive = False
            else:
                self.ai_snake.insert(0, new_head)
                
                # Check if ate food
                if new_head == self.food:
                    self.ai_score += self.FOOD_SCORE
                    self.food = self.spawn_food()
                else:
                    self.ai_snake.pop()
                
                # Check if hit player snake
                if new_head in self.player_snake:
                    self.ai_alive = False
        
        # Check game over
        if not self.player_alive or not self.ai_alive:
            self.game_over = True
            if self.player_alive and not self.ai_alive:
                self.winner = 'player'
            elif self.ai_alive and not self.player_alive:
                self.winner = 'ai'
            else:
                # Both dead, higher score wins
                if self.player_score > self.ai_score:
                    self.winner = 'player'
                elif self.ai_score > self.player_score:
                    self.winner = 'ai'
                else:
                    self.winner = 'tie'
        
        self.tick += 1
    
    def to_dict(self):
        """Convert to dictionary for JSON"""
        return {
            'player_snake': self.player_snake,
            'ai_snake': self.ai_snake,
            'food': self.food,
            'player_score': self.player_score,
            'ai_score': self.ai_score,
            'player_alive': self.player_alive,
            'ai_alive': self.ai_alive,
            'game_over': self.game_over,
            'winner': self.winner,
            'tick': self.tick,
            'board_size': self.BOARD_SIZE
        }


HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snake AI Game</title>
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
            padding: 20px;
        }

        .container {
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            text-align: center;
            max-width: 900px;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }

        .game-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }

        .score-box {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .score-label {
            font-size: 12px;
            color: #999;
            text-transform: uppercase;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .score-value {
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }

        .ai-box {
            border-left-color: #f44336;
        }

        .game-board {
            background: #222;
            border: 3px solid #333;
            margin: 20px auto;
            display: inline-block;
            position: relative;
            aspect-ratio: 1;
            width: 500px;
            max-width: 90vw;
        }

        .game-cell {
            position: absolute;
            border: 0.5px solid #444;
        }

        .player-segment {
            background: #4caf50;
            box-shadow: 0 0 5px rgba(76, 175, 80, 0.6);
        }

        .ai-segment {
            background: #f44336;
            box-shadow: 0 0 5px rgba(244, 67, 54, 0.6);
        }

        .food {
            background: #ffc107;
            border-radius: 50%;
            box-shadow: 0 0 8px rgba(255, 193, 7, 0.8);
        }

        .message {
            background: #e3f2fd;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            color: #333;
            font-weight: 500;
            font-size: 16px;
        }

        .message.game-over {
            background: #fff3cd;
            border-left-color: #ffc107;
        }

        .message.player-wins {
            background: #d4edda;
            border-left-color: #4caf50;
        }

        .message.ai-wins {
            background: #f8d7da;
            border-left-color: #f44336;
        }

        .controls {
            margin: 20px 0;
        }

        .control-info {
            color: #666;
            margin-bottom: 10px;
            font-size: 14px;
        }

        button {
            padding: 12px 25px;
            font-size: 14px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: bold;
        }

        .btn-new {
            background: #667eea;
            color: white;
            margin-top: 15px;
        }

        .btn-new:hover {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .info {
            color: #999;
            font-size: 13px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }

        .arrow-keys {
            display: grid;
            grid-template-columns: repeat(3, 40px);
            gap: 10px;
            margin: 15px auto;
            width: fit-content;
        }

        .arrow-btn {
            width: 40px;
            height: 40px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            user-select: none;
        }

        .arrow-btn:active {
            background: #764ba2;
            transform: scale(0.95);
        }

        .arrow-btn.spacer {
            visibility: hidden;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐍 Snake AI Battle</h1>
        <p class="subtitle">Compete against an intelligent AI snake!</p>

        <div class="game-info">
            <div class="score-box">
                <div class="score-label">Your Score</div>
                <div class="score-value" id="playerScore">0</div>
            </div>
            <div class="score-box ai-box">
                <div class="score-label">AI Score</div>
                <div class="score-value" id="aiScore">0</div>
            </div>
        </div>

        <div class="game-board" id="gameBoard"></div>

        <div class="message" id="message">Game running...</div>

        <div class="controls">
            <div class="control-info">Use Arrow Keys or WASD to move</div>
            <div class="arrow-keys">
                <button class="arrow-btn spacer"></button>
                <button class="arrow-btn" id="upBtn" onclick="move(0, -1)">↑</button>
                <button class="arrow-btn spacer"></button>
                
                <button class="arrow-btn" id="leftBtn" onclick="move(-1, 0)">←</button>
                <button class="arrow-btn spacer"></button>
                <button class="arrow-btn" id="rightBtn" onclick="move(1, 0)">→</button>

                <button class="arrow-btn spacer"></button>
                <button class="arrow-btn" id="downBtn" onclick="move(0, 1)">↓</button>
                <button class="arrow-btn spacer"></button>
            </div>
        </div>

        <button class="btn-new" onclick="newGame()">New Game</button>

        <div class="info">
            🎮 Help your snake grow by eating food 🍌<br>
            💡 Avoid walls, yourself, and the AI snake!
        </div>
    </div>

    <script>
        let gameState = null;
        let gameRunning = true;
        let gameLoopId = null;

        const CELL_SIZE_PERCENT = 100 / 20; // Board has 20x20 cells

        async function loadGame() {
            try {
                const response = await fetch('/api/game');
                gameState = await response.json();
                render();
                updateMessage();
            } catch (error) {
                console.error('Error loading game:', error);
            }
        }

        function render() {
            const board = document.getElementById('gameBoard');
            board.innerHTML = '';

            // Calculate cell size
            const boardSize = board.offsetWidth;
            const cellSize = boardSize / 20;

            // Render player snake (green)
            gameState.player_snake.forEach((segment, idx) => {
                const cell = document.createElement('div');
                cell.className = 'game-cell player-segment';
                if (idx === 0) cell.style.borderRadius = '3px';
                cell.style.width = cellSize + 'px';
                cell.style.height = cellSize + 'px';
                cell.style.left = (segment[0] * cellSize) + 'px';
                cell.style.top = (segment[1] * cellSize) + 'px';
                board.appendChild(cell);
            });

            // Render AI snake (red)
            gameState.ai_snake.forEach((segment, idx) => {
                const cell = document.createElement('div');
                cell.className = 'game-cell ai-segment';
                if (idx === 0) cell.style.borderRadius = '3px';
                cell.style.width = cellSize + 'px';
                cell.style.height = cellSize + 'px';
                cell.style.left = (segment[0] * cellSize) + 'px';
                cell.style.top = (segment[1] * cellSize) + 'px';
                board.appendChild(cell);
            });

            // Render food
            const foodCell = document.createElement('div');
            foodCell.className = 'game-cell food';
            foodCell.style.width = (cellSize * 0.8) + 'px';
            foodCell.style.height = (cellSize * 0.8) + 'px';
            foodCell.style.left = (gameState.food[0] * cellSize + cellSize * 0.1) + 'px';
            foodCell.style.top = (gameState.food[1] * cellSize + cellSize * 0.1) + 'px';
            board.appendChild(foodCell);

            // Update scores
            document.getElementById('playerScore').textContent = gameState.player_score;
            document.getElementById('aiScore').textContent = gameState.ai_score;
        }

        function updateMessage() {
            const msgDiv = document.getElementById('message');
            msgDiv.className = 'message';

            if (gameState.game_over) {
                if (gameState.winner === 'player') {
                    msgDiv.className = 'message game-over player-wins';
                    msgDiv.textContent = '🎉 You won! Your snake survived!';
                } else if (gameState.winner === 'ai') {
                    msgDiv.className = 'message game-over ai-wins';
                    msgDiv.textContent = '💀 AI won! Your snake crashed!';
                } else {
                    msgDiv.className = 'message game-over';
                    msgDiv.textContent = '⚖️ Tie! Both snakes crashed!';
                }
                gameRunning = false;
            } else {
                msgDiv.textContent = 'Game running... Tick: ' + gameState.tick;
            }
        }

        async function move(dx, dy) {
            if (!gameRunning) return;

            try {
                const response = await fetch('/api/move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ dx, dy })
                });

                gameState = await response.json();
                render();
                updateMessage();
            } catch (error) {
                console.error('Error:', error);
            }
        }

        async function gameLoop() {
            if (!gameRunning || !gameState) return;

            try {
                const response = await fetch('/api/tick', { method: 'POST' });
                gameState = await response.json();
                render();
                updateMessage();
            } catch (error) {
                console.error('Error:', error);
            }
        }

        async function newGame() {
            try {
                const response = await fetch('/api/reset', { method: 'POST' });
                gameState = await response.json();
                gameRunning = true;
                render();
                updateMessage();
            } catch (error) {
                console.error('Error:', error);
            }
        }

        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            if (!gameRunning) return;

            switch(e.key.toLowerCase()) {
                case 'arrowup':
                case 'w':
                    e.preventDefault();
                    move(0, -1);
                    break;
                case 'arrowdown':
                case 's':
                    e.preventDefault();
                    move(0, 1);
                    break;
                case 'arrowleft':
                case 'a':
                    e.preventDefault();
                    move(-1, 0);
                    break;
                case 'arrowright':
                case 'd':
                    e.preventDefault();
                    move(1, 0);
                    break;
            }
        });

        loadGame();
        gameLoopId = setInterval(gameLoop, 150); // Update every 150ms
    </script>
</body>
</html>
'''


game = SnakeGame()


class SnakeHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for Snake game"""
    
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
            self.wfile.write(json.dumps(game.to_dict()).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/move':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(content_length).decode())
                dx = body.get('dx', 0)
                dy = body.get('dy', 0)
                
                game.update(player_direction=(dx, dy))
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(game.to_dict()).encode())
            except Exception as e:
                print(f"Error in /api/move: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        elif self.path == '/api/tick':
            try:
                game.update()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(game.to_dict()).encode())
            except Exception as e:
                print(f"Error in /api/tick: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        elif self.path == '/api/reset':
            try:
                game.reset()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(game.to_dict()).encode())
            except Exception as e:
                print(f"Error in /api/reset: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress logging"""
        pass


def start_server(port=8765):
    """Start the Snake AI web server"""
    try:
        with socketserver.TCPServer(("", port), SnakeHandler) as httpd:
            print(f"\n🐍 Snake AI Battle server running at http://localhost:{port}")
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
    parser = argparse.ArgumentParser(description="Snake AI Battle Game")
    parser.add_argument("--port", type=int, default=8765, help="Port to run server on")
    args = parser.parse_args()
    
    start_server(args.port)
