from flask import Flask, request, jsonify

app = Flask(__name__)
commands = {}

@app.route('/send', methods=['POST'])
def send_command():
    data = request.get_json()
    target = data.get('to')
    command = {
        "command": data.get('command'),
        "args": data.get('args')
    }
    if not target or not command["command"]:
        return jsonify({"error": "Invalid command data"}), 400
    if target not in commands:
        commands[target] = []
    commands[target].append(command)
    return jsonify({"status": "queued", "to": target})

@app.route('/poll/<userid>')
def poll(userid):
    cmds = commands.get(userid, [])
    commands[userid] = []
    return jsonify(cmds)

@app.route('/disconnect', methods=['POST'])
def disconnect():
    data = request.get_json()
    userid = data.get('userid')
    return jsonify({"status": "disconnected", "userid": userid})

if __name__ == '__main__':
    app.run(debug=True)
