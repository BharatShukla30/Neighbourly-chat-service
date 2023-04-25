from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import mongo_connection
from datetime import datetime, timezone
from pymongo import DESCENDING
from bson import json_util
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
db = mongo_connection.get_db()  # Use the 'neighbourly' database
message_history = db['messages']  # Use the 'messages' collection

# Initialize SocketIO
socketio = SocketIO(app)

# Store chat messages in memory
messages = []

@app.route('/')
def index():
    return render_template('index.html')

# Route for sending a message
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json  # Get JSON data from the request
    room_id = data['room_id']
    sender = data['sender']
    receiver = data['receiver']
    message = data['message']
    timestamp = datetime.now(timezone.utc)

    message_data = {
        'room_id': room_id,
        'sender': sender,
        'receiver': [],
        'read_by': [],
        'message': message,
        'timestamp': timestamp
    }

    message_history.insert_one(message_data)

    # Emit the new message to all connected clients via SocketIO
    socketio.emit('message', message_data, broadcast=True)

    return jsonify({'status': 'success', 'message': 'Message sent'})


# Route for getting messages for a particular recipient
@app.route('/get_messages/<room_id>', methods=['GET'])
def get_messages(room_id):
    # Get the skip parameter from the request query string
    skip = int(request.args.get('skip', 0))

    # Find all messages in the messages collection where room_id matches,
    # sorted by timestamp in reverse order, limited to 2 messages, and skipped by the specified number
    messages = list(message_history.find({'room_id': str(room_id)})
                    .sort('timestamp', DESCENDING)
                    .skip(skip)
                    .limit(50))
    json_messages = json_util.dumps(messages)
    return jsonify({'status': 'success', 'messages': json_messages})

@socketio.on('connect')
def on_connect():
    print('Client connected')
    # Send existing messages to the newly connected client
    emit('messages', messages)

@socketio.on('disconnect')
def on_disconnect():
    print('Client disconnected')

@socketio.on('message')
def on_message(data):
    print('Received message:', data)
    messages.append(data)  # Store the message in memory
    emit('message', data, broadcast=True)  # Broadcast the message to all connected clients

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
