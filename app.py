from flask import Flask, request, jsonify
from threading import Lock, Thread
import time

app = Flask(__name__)
commands = {}
active_users = {}
lock = Lock()

USER_TIMEOUT = 10

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

    with lock:
        if target not in commands:
            commands[target] = []
        commands[target].append(command)

    return jsonify({"status": "queued", "to": target})

@app.route('/poll/<userid>')
def poll(userid):
    with lock:
        active_users[str(userid)] = time.time()
        cmds = commands.get(str(userid), [])
        commands[str(userid)] = []
    return jsonify(cmds)

@app.route('/active')
def get_active_users():
    with lock:
        return jsonify(list(active_users.keys()))

@app.route('/disconnect', methods=['POST'])
def disconnect():
    data = request.get_json()
    userid = str(data.get('userid'))
    with lock:
        active_users.pop(userid, None)
    return jsonify({"status": "disconnected", "userid": userid})

def cleanup_inactive_users():
    while True:
        time.sleep(5)
        now = time.time()
        with lock:
            print(f"[Cleanup] Active users before cleanup: {list(active_users.keys())}")
            inactive = [uid for uid, last_seen in active_users.items() if now - last_seen > USER_TIMEOUT]
            if inactive:
                print(f"[Cleanup] Removing inactive users: {inactive}")
            for uid in inactive:
                del active_users[uid]
            print(f"[Cleanup] Active users after cleanup: {list(active_users.keys())}")

Thread(target=cleanup_inactive_users, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)
