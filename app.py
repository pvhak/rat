from flask import Flask, request, jsonify

app = Flask(__name__)

commands = {
    "8662592387": [
        {"command": "print", "args": "hi"},
    ]
}

@app.route('/poll/<userid>')
def poll(userid):
    username = request.args.get('username')
    gameid = request.args.get('gameid')
    jobid = request.args.get('jobid')
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
