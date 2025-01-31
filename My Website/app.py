from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Store active usernames
active_users = set()

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

@socketio.on('set_username')
def handle_set_username(username):
    if username in active_users:
        emit('set_username', {'success': False}, room=request.sid)  # Send only to the requesting user
    else:
        active_users.add(username)
        emit('set_username', {'success': True}, room=request.sid)  # Confirm username to the requesting user


@socketio.on('send_message')
def handle_send_message(data):
    emit('receive_message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
