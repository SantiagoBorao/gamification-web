from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = "data/users.json"

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/users", methods=["GET", "POST"])
def users():
    users = load_users()

    if request.method == "POST":
        new_name = request.form.get("username")
        if new_name and new_name not in users:
            users[new_name] = {"skills": {}}
            save_users(users)
        return redirect(url_for("users"))

    return render_template("users.html", users=users)

if __name__ == "__main__":
    app.run(debug=True)
