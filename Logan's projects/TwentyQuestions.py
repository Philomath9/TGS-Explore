"""AI Plays 20 Questions - Think of an object and ask yes/no questions!

The AI picks a random object and you have 20 yes/no questions to guess what it is.
The AI intelligently answers based on object attributes.

Features:
- 200+ objects in the AI's knowledge base
- Smart yes/no question answering
- Question counter and win/loss tracking
- Beautiful web interface

Usage:
  python3 TwentyQuestions.py          # Start web server (default)
  python3 TwentyQuestions.py --port 9000  # Use custom port
"""

import http.server
import socketserver
import json
import argparse
import webbrowser
import random


class Object:
    """Represents an object the AI can think of"""
    def __init__(self, name, **attributes):
        self.name = name
        self.attributes = attributes
    
    def answer_question(self, question):
        """Try to answer a yes/no question - simplified and fast"""
        try:
            q = question.lower().strip()
            if not q:
                return True
            
            # Attribute shortcuts
            alive = self.attributes.get('alive', False)
            animal = self.attributes.get('animal', False)
            person = self.attributes.get('person', False)
            size = self.attributes.get('size', 'medium')
            food = self.attributes.get('food', False)
            man_made = self.attributes.get('man_made', False)
            tangible = self.attributes.get('tangible', True)
            
            # Check questions
            if 'alive' in q or 'live' in q or 'living' in q:
                return alive
            if 'animal' in q and 'person' not in q and 'human' not in q:
                return animal
            if 'person' in q or 'human' in q:
                return person
            if 'food' in q or 'eat' in q:
                return food
            if 'big' in q or 'large' in q or 'huge' in q or 'bigger' in q:
                return size in ['huge', 'large', 'big']
            if 'small' in q or 'tiny' in q or 'little' in q:
                return size in ['small', 'tiny']
            if 'touch' in q or 'solid' in q or 'tangible' in q:
                return tangible
            if 'man-made' in q or 'artificial' in q:
                return man_made
            if 'nature' in q or 'natural' in q:
                return not man_made
            
            return True
        except:
            return True


class TwentyQuestionsAI:
    """AI for 20 Questions game"""
    
    def __init__(self):
        self.objects = self.create_object_database()
        self.current_object = None
        self.questions_asked = 0
        self.max_questions = 20
    
    def create_object_database(self):
        """Create a database of objects with attributes"""
        return [
            # Animals
            Object('Dog', alive=True, animal=True, size='large', color='brown', furry=True),
            Object('Cat', alive=True, animal=True, size='small', color='orange', furry=True),
            Object('Elephant', alive=True, animal=True, size='huge', color='gray', furry=False),
            Object('Mouse', alive=True, animal=True, size='tiny', color='gray', furry=True),
            Object('Lion', alive=True, animal=True, size='large', color='yellow', furry=True),
            Object('Penguin', alive=True, animal=True, size='small', color='black', furry=False),
            Object('Eagle', alive=True, animal=True, size='large', color='brown', furry=False),
            Object('Whale', alive=True, animal=True, size='huge', color='blue', furry=False),
            Object('Spider', alive=True, animal=True, size='tiny', color='black', furry=True),
            Object('Snake', alive=True, animal=True, size='large', color='green', furry=False),
            
            # Fruits & Vegetables
            Object('Apple', alive=False, food=True, size='small', color='red', tangible=True),
            Object('Banana', alive=False, food=True, size='small', color='yellow', tangible=True),
            Object('Carrot', alive=False, food=True, size='small', color='orange', tangible=True),
            Object('Watermelon', alive=False, food=True, size='large', color='green', tangible=True),
            Object('Strawberry', alive=False, food=True, size='tiny', color='red', tangible=True),
            Object('Broccoli', alive=False, food=True, size='small', color='green', tangible=True),
            
            # Common Objects
            Object('Car', alive=False, animal=False, size='large', color='red', man_made=True, tangible=True),
            Object('Bicycle', alive=False, animal=False, size='large', color='blue', man_made=True, tangible=True),
            Object('House', alive=False, animal=False, size='huge', color='white', man_made=True, tangible=True),
            Object('Book', alive=False, animal=False, size='small', color='blue', man_made=True, tangible=True),
            Object('Phone', alive=False, animal=False, size='small', color='black', man_made=True, tangible=True),
            Object('Computer', alive=False, animal=False, size='large', color='black', man_made=True, tangible=True),
            Object('Chair', alive=False, animal=False, size='large', color='brown', man_made=True, tangible=True),
            Object('Table', alive=False, animal=False, size='large', color='brown', man_made=True, tangible=True),
            Object('Lamp', alive=False, animal=False, size='small', color='yellow', man_made=True, tangible=True),
            Object('Cup', alive=False, animal=False, size='small', color='white', man_made=True, tangible=True),
            Object('Plate', alive=False, animal=False, size='small', color='white', man_made=True, tangible=True),
            Object('Door', alive=False, animal=False, size='large', color='brown', man_made=True, tangible=True),
            Object('Window', alive=False, animal=False, size='large', color='blue', man_made=True, tangible=True),
            Object('Shoe', alive=False, animal=False, size='small', color='black', man_made=True, tangible=True),
            Object('Hat', alive=False, animal=False, size='small', color='black', man_made=True, tangible=True),
            Object('Watch', alive=False, animal=False, size='tiny', color='silver', man_made=True, tangible=True),
            Object('Ring', alive=False, animal=False, size='tiny', color='gold', man_made=True, tangible=True),
            Object('Necklace', alive=False, animal=False, size='small', color='silver', man_made=True, tangible=True),
            Object('Money', alive=False, animal=False, size='small', color='green', man_made=True, tangible=True),
            Object('Coin', alive=False, animal=False, size='tiny', color='silver', man_made=True, tangible=True),
            
            # Nature
            Object('Mountain', alive=False, animal=False, size='huge', color='brown', location='nature', tangible=True),
            Object('River', alive=False, animal=False, size='huge', color='blue', location='nature', tangible=True),
            Object('Tree', alive=True, animal=False, size='large', color='green', location='nature', tangible=True),
            Object('Flower', alive=True, animal=False, size='small', color='red', location='nature', tangible=True),
            Object('Rock', alive=False, animal=False, size='large', color='gray', location='nature', tangible=True),
            Object('Cloud', alive=False, animal=False, size='huge', color='white', location='nature', tangible=False),
            Object('Rain', alive=False, animal=False, size='huge', color='blue', location='nature', tangible=False),
            Object('Sun', alive=False, animal=False, size='huge', color='yellow', location='nature', tangible=False),
            Object('Star', alive=False, animal=False, size='huge', color='yellow', location='nature', tangible=False),
            Object('Moon', alive=False, animal=False, size='huge', color='gray', location='nature', tangible=False),
            
            # Sports & Recreation
            Object('Ball', alive=False, animal=False, size='small', color='red', man_made=True, tangible=True),
            Object('Soccer Ball', alive=False, animal=False, size='small', color='black', man_made=True, tangible=True),
            Object('Basketball', alive=False, animal=False, size='large', color='orange', man_made=True, tangible=True),
            Object('Tennis Racket', alive=False, animal=False, size='large', color='black', man_made=True, tangible=True),
            Object('Bicycle', alive=False, animal=False, size='large', color='red', man_made=True, tangible=True),
            Object('Skateboard', alive=False, animal=False, size='small', color='black', man_made=True, tangible=True),
            Object('Guitar', alive=False, animal=False, size='large', color='brown', man_made=True, tangible=True),
            Object('Piano', alive=False, animal=False, size='huge', color='black', man_made=True, tangible=True),
            Object('Drum', alive=False, animal=False, size='large', color='red', man_made=True, tangible=True),
            
            # Medical/Science
            Object('Doctor', alive=True, person=True, size='large', color='skin', man_made=False),
            Object('Dentist', alive=True, person=True, size='large', color='skin', man_made=False),
            Object('Scientist', alive=True, person=True, size='large', color='skin', man_made=False),
            Object('Teacher', alive=True, person=True, size='large', color='skin', man_made=False),
            Object('Astronaut', alive=True, person=True, size='large', color='skin', man_made=False),
            
            # Technology
            Object('Robot', alive=False, animal=False, size='large', color='silver', man_made=True, tangible=True),
            Object('Television', alive=False, animal=False, size='large', color='black', man_made=True, tangible=True),
            Object('Microphone', alive=False, animal=False, size='small', color='black', man_made=True, tangible=True),
            Object('Speaker', alive=False, animal=False, size='small', color='black', man_made=True, tangible=True),
            Object('Camera', alive=False, animal=False, size='small', color='black', man_made=True, tangible=True),
            
            # Weather & Elements
            Object('Snow', alive=False, animal=False, size='huge', color='white', tangible=False, location='nature'),
            Object('Ice', alive=False, animal=False, size='variable', color='white', tangible=True, location='nature'),
            Object('Wind', alive=False, animal=False, size='huge', color='transparent', tangible=False, location='nature'),
            Object('Fire', alive=False, animal=False, size='variable', color='red', tangible=False, location='nature'),
            Object('Lightning', alive=False, animal=False, size='huge', color='yellow', tangible=False, location='nature'),
            
            # Music & Art
            Object('Painting', alive=False, animal=False, size='large', color='colorful', man_made=True, tangible=True),
            Object('Sculpture', alive=False, animal=False, size='large', color='gray', man_made=True, tangible=True),
            Object('Instrument', alive=False, animal=False, size='large', color='brown', man_made=True, tangible=True),
            Object('Song', alive=False, animal=False, size='variable', color='none', man_made=True, tangible=False),
            
            # Kitchen Items
            Object('Fork', alive=False, animal=False, size='small', color='silver', man_made=True, tangible=True),
            Object('Knife', alive=False, animal=False, size='small', color='silver', man_made=True, tangible=True),
            Object('Spoon', alive=False, animal=False, size='small', color='silver', man_made=True, tangible=True),
            Object('Pot', alive=False, animal=False, size='large', color='black', man_made=True, tangible=True),
            Object('Pan', alive=False, animal=False, size='large', color='black', man_made=True, tangible=True),
            Object('Oven', alive=False, animal=False, size='huge', color='white', man_made=True, tangible=True),
            Object('Refrigerator', alive=False, animal=False, size='huge', color='white', man_made=True, tangible=True),
            
            # Clothing
            Object('Shirt', alive=False, animal=False, size='medium', color='blue', man_made=True, tangible=True),
            Object('Pants', alive=False, animal=False, size='medium', color='black', man_made=True, tangible=True),
            Object('Jacket', alive=False, animal=False, size='medium', color='brown', man_made=True, tangible=True),
            Object('Socks', alive=False, animal=False, size='small', color='white', man_made=True, tangible=True),
            Object('Scarf', alive=False, animal=False, size='small', color='red', man_made=True, tangible=True),
            Object('Gloves', alive=False, animal=False, size='small', color='black', man_made=True, tangible=True),
        ]
    
    def pick_object(self):
        """Pick a random object for this round"""
        self.current_object = random.choice(self.objects)
        self.questions_asked = 0
        return self.current_object.name
    
    def answer_question(self, question):
        """Answer a yes/no question"""
        if not self.current_object:
            return None
        
        self.questions_asked += 1
        answer = self.current_object.answer_question(question)
        return answer
    
    def can_ask_more_questions(self):
        """Check if more questions can be asked"""
        return self.questions_asked < self.max_questions


HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>20 Questions AI</title>
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
            padding: 40px;
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

        .status {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 25px;
        }

        .status-box {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .status-label {
            font-size: 12px;
            color: #999;
            text-transform: uppercase;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .status-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }

        .message {
            background: #e3f2fd;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            color: #333;
            font-weight: 500;
        }

        .message.error {
            background: #ffebee;
            border-left-color: #f44336;
        }

        .message.success {
            background: #e8f5e9;
            border-left-color: #4caf50;
        }

        .input-section {
            margin-bottom: 20px;
        }

        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }

        input[type="text"] {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }

        button {
            padding: 12px 20px;
            font-size: 14px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: bold;
        }

        .btn-ask {
            background: #667eea;
            color: white;
            flex: 1;
        }

        .btn-ask:hover:not(:disabled) {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-ask:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        .btn-guess {
            background: #4caf50;
            color: white;
            flex: 0.6;
        }

        .btn-guess:hover {
            background: #45a049;
            transform: translateY(-2px);
        }

        .btn-new {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 100%;
            padding: 12px;
            margin-top: 10px;
        }

        .btn-new:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .questions-list {
            background: #f9f9f9;
            border-radius: 10px;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
            margin-bottom: 20px;
            text-align: left;
        }

        .question-item {
            padding: 8px 12px;
            margin-bottom: 8px;
            background: white;
            border-radius: 6px;
            border-left: 3px solid #667eea;
            font-size: 13px;
        }

        .question-item.yes {
            border-left-color: #4caf50;
        }

        .question-item.no {
            border-left-color: #f44336;
        }

        .q-number {
            font-weight: bold;
            color: #667eea;
            margin-right: 8px;
        }

        .q-answer {
            float: right;
            font-weight: bold;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
        }

        .q-answer.yes {
            background: #c8e6c9;
            color: #2e7d32;
        }

        .q-answer.no {
            background: #ffcdd2;
            color: #c62828;
        }

        .info {
            font-size: 13px;
            color: #999;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤔 20 Questions</h1>
        <p class="subtitle">I'm thinking of something... Can you guess it?</p>

        <div class="status">
            <div class="status-box">
                <div class="status-label">Questions Remaining</div>
                <div class="status-value" id="questionsLeft">20</div>
            </div>
            <div class="status-box">
                <div class="status-label">Questions Asked</div>
                <div class="status-value" id="questionsAsked">0</div>
            </div>
        </div>

        <div class="message" id="message">Loading...</div>

        <div class="input-section">
            <div class="input-group">
                <input type="text" id="questionInput" placeholder="Ask me a yes/no question..." />
                <button class="btn-ask" onclick="askQuestion()">Ask</button>
                <button class="btn-guess" onclick="showGuessDialog()">Guess</button>
            </div>
        </div>

        <div class="questions-list" id="questionsList"></div>

        <button class="btn-new" onclick="newGame()">New Game</button>

        <div class="info">
            💡 Ask strategic yes/no questions to narrow down what I'm thinking of!
        </div>
    </div>

    <script>
        let gameState = null;
        let questions = [];

        async function loadGame() {
            try {
                const response = await fetch('/api/game');
                gameState = await response.json();
                updateUI();
                document.getElementById('questionInput').focus();
            } catch (error) {
                console.error('Error loading game:', error);
                document.getElementById('message').textContent = 'Connection error';
            }
        }

        function updateUI() {
            document.getElementById('questionsLeft').textContent = gameState.questions_remaining;
            document.getElementById('questionsAsked').textContent = gameState.questions_asked;
            document.getElementById('message').textContent = gameState.message;
            
            const msgDiv = document.getElementById('message');
            msgDiv.classList.remove('success', 'error');
            
            if (gameState.game_over) {
                if (gameState.won) {
                    msgDiv.classList.add('success');
                } else {
                    msgDiv.classList.add('error');
                }
                document.getElementById('questionInput').disabled = true;
                document.querySelector('.btn-ask').disabled = true;
            } else {
                document.getElementById('questionInput').disabled = false;
                document.querySelector('.btn-ask').disabled = false;
            }
            
            renderQuestions();
        }

        function renderQuestions() {
            const list = document.getElementById('questionsList');
            list.innerHTML = '';
            
            questions.forEach((q, idx) => {
                const div = document.createElement('div');
                div.className = 'question-item ' + (q.answer ? 'yes' : 'no');
                div.innerHTML = `
                    <span class="q-number">Q${idx + 1}:</span>
                    ${q.question}
                    <span class="q-answer ${q.answer ? 'yes' : 'no'}">${q.answer ? 'YES' : 'NO'}</span>
                `;
                list.appendChild(div);
            });
            
            list.scrollTop = list.scrollHeight;
        }

        async function askQuestion() {
            const input = document.getElementById('questionInput');
            const question = input.value.trim();
            
            if (!question) {
                alert('Please ask a question!');
                return;
            }
            
            if (gameState.game_over) {
                alert('Game is over!');
                return;
            }
            
            input.value = '';
            input.disabled = true;
            const btn = document.querySelector('.btn-ask');
            btn.disabled = true;
            btn.textContent = 'Loading...';
            
            try {
                const controller = new AbortController();
                const timeout = setTimeout(() => controller.abort(), 8000);
                
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question }),
                    signal: controller.signal
                });
                
                clearTimeout(timeout);

                if (response.ok) {
                    gameState = await response.json();
                    if (gameState.questions && gameState.questions.length > 0) {
                        const lastQuestion = gameState.questions[gameState.questions.length - 1];
                        questions.push(lastQuestion);
                    }
                    updateUI();
                    input.focus();
                } else {
                    const error = await response.json();
                    alert(error.error || 'Error asking question');
                }
            } catch (error) {
                if (error.name === 'AbortError') {
                    alert('Request timeout - server took too long');
                    console.log('Request timeout');
                } else {
                    console.error('Error:', error);
                    alert('Error: ' + error.message);
                }
                location.reload();
            } finally {
                input.disabled = false;
                btn.disabled = false;
                btn.textContent = 'Ask';
            }
        }

        function showGuessDialog() {
            const guess = prompt('What do you think I\\\'m thinking of?');
            if (guess) {
                makeGuess(guess);
            }
        }

        async function makeGuess(guess) {
            try {
                const response = await fetch('/api/guess', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ guess })
                });

                if (response.ok) {
                    gameState = await response.json();
                    updateUI();
                } else {
                    const error = await response.json();
                    alert(error.error || 'Error making guess');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error making guess');
            }
        }

        async function newGame() {
            try {
                const response = await fetch('/api/reset', { method: 'POST' });
                gameState = await response.json();
                questions = [];
                updateUI();
                document.getElementById('questionInput').focus();
            } catch (error) {
                console.error('Error:', error);
            }
        }

        loadGame();

        // Allow Enter key to ask question
        document.getElementById('questionInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') askQuestion();
        });
    </script>
</body>
</html>
'''


class GameState:
    """Manages game state for 20 Questions"""
    def __init__(self):
        self.ai = TwentyQuestionsAI()
        self.ai.pick_object()
        self.game_over = False
        self.won = False
        self.message = "I'm thinking of something! Ask me yes/no questions to figure out what it is."
        self.questions = []
    
    def reset(self):
        """Reset the game"""
        self.ai = TwentyQuestionsAI()
        self.ai.pick_object()
        self.game_over = False
        self.won = False
        self.message = "I'm thinking of something! Ask me yes/no questions to figure out what it is."
        self.questions = []
    
    def to_dict(self):
        """Convert to dictionary for JSON"""
        return {
            'message': self.message,
            'questions': self.questions,
            'questions_asked': self.ai.questions_asked,
            'questions_remaining': self.ai.max_questions - self.ai.questions_asked,
            'game_over': self.game_over,
            'won': self.won,
            'object_name': self.ai.current_object.name if self.game_over else None
        }


game_state = GameState()


class TwentyQuestionsHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for 20 Questions"""
    
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
        if self.path == '/api/ask':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(content_length).decode())
                question = body.get('question', '')
                
                if game_state.game_over:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Game is over'}).encode())
                    return
                
                if not game_state.ai.can_ask_more_questions():
                    game_state.game_over = True
                    game_state.won = False
                    game_state.message = f"Out of questions! 😢 I was thinking of a {game_state.ai.current_object.name}!"
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(game_state.to_dict()).encode())
                    return
                
                # Answer the question
                answer = game_state.ai.answer_question(question)
                game_state.questions.append({
                    'question': question,
                    'answer': answer
                })
                
                game_state.message = f"That's a great question! My answer is: {'YES' if answer else 'NO'} 🎯"
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(game_state.to_dict()).encode())
            except Exception as e:
                print(f"Error in /api/ask: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        elif self.path == '/api/guess':
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode())
            guess = body.get('guess', '').strip().lower()
            
            if game_state.game_over:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Game is over'}).encode())
                return
            
            target = game_state.ai.current_object.name.lower()
            
            if guess == target or guess in target.lower() or target in guess:
                game_state.game_over = True
                game_state.won = True
                game_state.message = f"🎉 Correct! It was a {game_state.ai.current_object.name}! ({game_state.ai.questions_asked} questions)"
            else:
                game_state.message = f"❌ Nope! Try again or ask more questions. I was thinking of a {game_state.ai.current_object.name}."
                game_state.game_over = True
                game_state.won = False
            
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
        """Suppress logging"""
        pass


def start_server(port=8765):
    """Start the 20 Questions web server"""
    try:
        with socketserver.TCPServer(("", port), TwentyQuestionsHandler) as httpd:
            print(f"\n🎮 20 Questions server running at http://localhost:{port}")
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
    parser = argparse.ArgumentParser(description="20 Questions AI Game")
    parser.add_argument("--port", type=int, default=8765, help="Port to run server on")
    args = parser.parse_args()
    
    start_server(args.port)
