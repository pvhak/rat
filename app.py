from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)
command_queue = defaultdict(list)

@app.route('/send/<userid>', methods=['POST'])
def send(userid):
    data = request.get_json()
    if not data or "command" not in data:
        return jsonify({"error": "Invalid data"}), 400
    command_queue[userid].append(data)
    return jsonify({"status": "queued"}), 200

@app.route('/poll/<userid>', methods=['GET'])
def poll(userid):
    cmds = command_queue.get(userid, [])
    command_queue[userid] = []
    return jsonify(cmds)

@app.route('/')
def home():
    return "Hello from Flask!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
