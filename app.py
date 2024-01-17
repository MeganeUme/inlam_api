from flask import Flask, request, render_template
import json

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello world"

@app.route("/tasks", methods=["GET"])
def get_tasks():
    with open("tasks.json", "r") as file:
        data = json.load(file)
    return data
    
@app.route("/tasks", methods=["POST"])
def add_tasks():
    with open("tasks.json", "w") as file:
        json.dump(request.form, file, indent=4)
    return "Task was added"


if __name__ == "__main__":
    app.run(debug=True)