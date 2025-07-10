from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)
command_queue = defaultdict(list)

@app.route('/poll/<userid>', methods=['GET'])
def poll(userid):
    commands = command_queue[userid]
    command_queue[userid] = []
    return jsonify(commands)

@app.route('/send/<userid>', methods=['POST'])
def send(userid):
    data = request.get_json()
    command_queue[userid].append(data)
    return jsonify({"status": "ok"})

@app.route('/disconnect', methods=['POST'])
def disconnect():
    data = request.get_json()
    userid = data.get('userid')
    if userid in command_queue:
        del command_queue[userid]
    return jsonify({"status": "disconnected"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
