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

@app.route("/user/<username>", methods=["GET", "POST"])
def user_profile(username):
    users = load_users()

    if username not in users:
        return f"User '{username}' not found.", 404

    user = users[username]

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_skill":
            skill_name = request.form.get("skill_name")
            if skill_name and skill_name not in user["skills"]:
                user["skills"][skill_name] = {"level": 1, "xp": 0}

        elif action == "add_xp":
            skill_name = request.form.get("skill_to_update")
            xp = int(request.form.get("xp_amount", 0))
            if skill_name in user["skills"]:
                skill = user["skills"][skill_name]
                skill["xp"] += xp
                level_threshold = 100 * skill["level"]
                while skill["xp"] >= level_threshold:
                    skill["xp"] -= level_threshold
                    skill["level"] += 1
                    level_threshold = 100 * skill["level"]

        save_users(users)
        return redirect(url_for("user_profile", username=username))

    return render_template("user_profile.html", username=username, skills=user["skills"])

# 👇 ESTA LÍNEA AL FINAL SIEMPRE
if __name__ == "__main__":
    app.run(debug=True)
