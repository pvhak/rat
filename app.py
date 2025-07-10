from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)
command_queue = defaultdict(list)
@app.route('/send/<userid>', methods=['POST', 'GET'])
def send(userid):
    if request.method == 'POST':
        data = request.get_json()
    else:
        data = {
            'command': request.args.get('command'),
            'args': request.args.get('args')
        }
    print(f"Received from {userid}: {data}")
    return jsonify({"status": "ok"})


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
