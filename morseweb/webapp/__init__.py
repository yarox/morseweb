from flask import Flask, jsonify, render_template


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/simulation/scene")
def get_scene():
    return jsonify({"foo": "bar"})
