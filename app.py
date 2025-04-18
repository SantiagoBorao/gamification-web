from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = "data/users.json"

# Utils to load and save user data
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

# Homepage
@app.route("/")
def home():
    return render_template("index.html")

# User list and creation
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

# User profile with skills
@app.route("/user/<username>", methods=["GET", "POST"])
def user_profile(username):
    users = load_users()

    if username not in users:
        return f"User '{username}' not found.", 404

    user = users[username]

    # Calcular estadísticas del usuario
    total_xp = 0
    top_skill = None
    max_xp = -1

    for skill_name, skill_data in user["skills"].items():
        total_xp += skill_data["xp"]
        if skill_data["xp"] > max_xp:
            top_skill = skill_name
            max_xp = skill_data["xp"]

    num_skills = len(user["skills"])


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

        elif action == "rename_skill":
            old_name = request.form.get("old_skill_name")
            new_name = request.form.get("new_skill_name")
            if old_name in user["skills"] and new_name and new_name not in user["skills"]:
                    user["skills"][new_name] = user["skills"].pop(old_name)
                    user["skills"][new_name]["name"] = new_name

        elif action == "delete_skill":
            skill_name = request.form.get("skill_to_delete")
            if skill_name in user["skills"]:
                del user["skills"][skill_name]

        elif action == "do_action":
            skill_name = request.form.get("skill_name")
            action_name = request.form.get("action_name")
            if skill_name in user["skills"]:
                skill = user["skills"][skill_name]
                if "actions" in skill and action_name in skill["actions"]:
                    xp = skill["actions"][action_name]
                    skill["xp"] += xp
                    level_threshold = 100 * skill["level"]
                    while skill["xp"] >= level_threshold:
                        skill["xp"] -= level_threshold
                        skill["level"] += 1
                        level_threshold = 100 * skill["level"]
        elif action == "add_action":
            skill_name = request.form.get("skill_name")
            action_name = request.form.get("new_action_name")
            try:
                xp = int(request.form.get("new_action_xp", 0))
            except:
                xp = 0
            if skill_name in user["skills"] and action_name and xp > 0:
                skill = user["skills"][skill_name]
                if "actions" not in skill:
                    skill["actions"] = {}
                skill["actions"][action_name] = xp

        save_users(users)
        return redirect(url_for("user_profile", username=username))

    return render_template(
        "user_profile.html",
        username=username,
        skills=user["skills"],
        total_xp=total_xp,
        num_skills=num_skills,
        top_skill=top_skill
    )



if __name__ == "__main__":
    app.run(debug=True)
