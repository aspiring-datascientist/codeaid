from flask import Flask, render_template, request, redirect, session, g, jsonify
import sqlite3
import requests
from flask_cors import CORS

app = Flask(__name__, template_folder="public")
CORS(app)

app.secret_key = "your_secret_key"
DATABASE = "users.db"

# Function to get database connection
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

# Close DB connection after request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# Home Page
@app.route("/")
def home():
    return render_template("home.html")

# Blog Page
@app.route("/blog")
def blog():
    return render_template("blog.html")

# About Page
@app.route("/about")
def about():
    return render_template("about.html")

# Achievements Page
@app.route("/achievements")
def achievements():
    return render_template("achievements.html")


# Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
            db.commit()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "Username or email already exists!"

    return render_template("signup.html")

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()

        if user:
            session["user_id"] = user["id"]
            return redirect("/index")
        else:
            return "Invalid credentials!"

    return render_template("login.html")

# Fetch GitHub Pull Request Diff
@app.route("/pulls", methods=["GET"])
def fetch_pull_data():
    owner = request.args.get("owner")
    repo = request.args.get("repo")
    pull_number = request.args.get("pull_number")

    if not owner or not repo or not pull_number:
        return jsonify({"error": "Missing parameters"}), 400

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
    try:
        response = requests.get(url, headers={"Accept": "application/vnd.github.v3.diff"})
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch pull request data"}), response.status_code
        return jsonify({"diff": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Logout Route
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/")

# Main Page
@app.route("/index")
def index():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("index.html")

if __name__ == "__main__":
 +   app.run(debug=True)
