#!/usr/bin/python3

from flask import Flask, request, send_from_directory
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return send_from_directory('templates', "tetris.html")

@app.route('/static/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

if __name__ == "__main__":
    app.run()
    # app.run(debug=True)
    # Debugging is needed sometimes (DANGERZONE)

