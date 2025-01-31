import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify, url_for
from flask_socketio import SocketIO, emit
import sqlite3
import json
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Database file located in the root
DB_FILE = "chat.db"

def init_db():
    """Create the database and table for messages."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

init_db()

# User data for chat (stored in a JSON file in the root)
USER_DATA_FILE = "user_data.json"
if os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "r") as f:
        active_users = json.load(f)
else:
    active_users = {}

def save_users():
    with open(USER_DATA_FILE, "w") as f:
        json.dump(active_users, f)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cv')
def cv():
    return render_template('cv.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/space')
def space():
    return render_template('space.html')

@app.route('/set_username', methods=['POST'])
def set_username():
    data = request.json
    username = data.get('username')
    device_id = data.get('device_id')
    if not username or not device_id:
        return jsonify({"success": False, "error": "Invalid data"})
    if username in active_users.values():
        return jsonify({"success": False, "error": "Username already taken"})
    active_users[device_id] = username
    save_users()
    return jsonify({"success": True, "username": username})

@app.route('/get_username', methods=['POST'])
def get_username():
    data = request.json
    device_id = data.get('device_id')
    if not device_id:
        return jsonify({"success": False})
    username = active_users.get(device_id)
    if username:
        return jsonify({"success": True, "username": username})
    else:
        return jsonify({"success": False})

@app.route('/get_messages', methods=['GET'])
def get_messages():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, message, timestamp FROM messages ORDER BY timestamp ASC")
        messages = cursor.fetchall()
    return jsonify([{"username": row[0], "message": row[1], "timestamp": row[2]} for row in messages])

@socketio.on('send_message')
def handle_send_message(data):
    device_id = data.get("device_id")
    username = active_users.get(device_id, "Unknown")
    message = data.get("message")
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, message))
        conn.commit()
    message_data = {"username": username, "message": message}
    emit('receive_message', message_data, broadcast=True)

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
