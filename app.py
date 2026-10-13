from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, csv, io, json
from datetime import datetime
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "stem_outreach.db")
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-for-local-demo")

QUESTIONS = [
    ("interest", "How interested are you in Science and Technology?", ["Very Interested", "Interested", "Moderately Interested", "Not Very Interested"]),
    ("hands_on", "Have you participated in hands-on STEM activities before?", ["Yes, many times", "Yes, once or twice", "Rarely", "Never"]),
    ("coding", "Have you heard about coding or programming?", ["Yes, and I understand it", "Heard about it, but know little", "Only heard the name", "Never heard about it"]),
    ("activity", "Which STEM activity would you prefer?", ["Science experiments", "Coding and computer games", "Electronics and circuits", "Engineering model building", "Mathematics puzzles"]),
    ("devices", "Do you have access to a smartphone or computer for learning?", ["Both smartphone and computer", "Smartphone only", "Computer only", "Neither"]),
    ("difficulty", "How difficult do you find Science and Mathematics?", ["Very easy", "Easy", "Moderate", "Difficult", "Very difficult"]),
    ("more_sessions", "Would you like more STEM learning sessions?", ["Definitely yes", "Probably yes", "Not sure", "No"]),
    ("tech_use", "How often do you use technology for learning?", ["Daily", "Several times a week", "Occasionally", "Never"]),
    ("career", "Are you aware of STEM career opportunities?", ["Very aware", "Somewhat aware", "Heard about a few careers", "Not aware"]),
    ("learning", "What is your preferred way to learn STEM?", ["Practical activities", "Videos and presentations", "Games and quizzes", "Textbooks and notes"]),
]

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student', created_at TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, respondent_code TEXT,
            answers_json TEXT NOT NULL, created_at TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
            category TEXT NOT NULL, duration TEXT NOT NULL, materials TEXT NOT NULL,
            steps TEXT NOT NULL, learning_outcome TEXT NOT NULL)""")
        count = conn.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
        if count == 0:
            seed = [
                ("Paper Bridge Challenge", "Engineering", "10 minutes", "Paper, tape, a few coins or erasers",
                 "Fold paper into different shapes; place it between two books; add one coin at a time; compare designs.",
                 "Students explore structure, testing and improvement."),
                ("Unplugged Algorithm Game", "Computing", "8 minutes", "Instruction cards or paper",
                 "One student gives step-by-step directions; another follows them; discuss ambiguous instructions.",
                 "Students understand sequence, instructions and debugging."),
                ("Maths Logic Puzzle", "Mathematics", "5 minutes", "Printed puzzle or whiteboard",
                 "Present a short age-appropriate puzzle; let small groups explain their reasoning.",
                 "Students practise logical reasoning and teamwork."),
                ("Everyday Technology & QR Codes", "Technology", "5 minutes", "Phone and teacher-approved learning link",
                 "Explain what a QR code does; scan only a teacher-approved, safe learning resource.",
                 "Students connect everyday technology with learning.")
            ]
            conn.executemany("INSERT INTO activities(title,category,duration,materials,steps,learning_outcome) VALUES(?,?,?,?,?,?)", seed)

init_db()

def current_user():
    if "user_id" not in session:
        return None
    with connect() as conn:
        return conn.execute("SELECT id,name,email,role FROM users WHERE id=?", (session["user_id"],)).fetchone()

@app.context_processor
def inject_user():
    return {"logged_user": current_user(), "year": datetime.now().year}

@app.route("/")
def index():
    return render_template("index.html", question_count=len(QUESTIONS))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter your name, a valid email, and a password of at least 8 characters.", "error")
            return render_template("register.html")
        try:
            with connect() as conn:
                conn.execute("INSERT INTO users(name,email,password_hash,role,created_at) VALUES(?,?,?,?,?)",
                             (name, email, generate_password_hash(password), "student", datetime.now().isoformat(timespec="seconds")))
            flash("Account created. You can now log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That email is already registered. Please log in.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with connect() as conn:
            user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if not current_user():
        return redirect(url_for("login"))
    with connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
        recent = conn.execute("SELECT id,respondent_code,created_at FROM responses ORDER BY id DESC LIMIT 5").fetchall()
        activities = conn.execute("SELECT * FROM activities ORDER BY id").fetchall()
    return render_template("dashboard.html", total=total, recent=recent, activities=activities)

@app.route("/survey", methods=["GET", "POST"])
def survey():
    if request.method == "POST":
        answers = {}
        for key, prompt, options in QUESTIONS:
            answer = request.form.get(key, "")
            if answer not in options:
                flash("Please answer every question using the provided choices.", "error")
                return render_template("survey.html", questions=QUESTIONS)
            answers[key] = answer
        respondent_code = request.form.get("respondent_code", "").strip()[:30] or "Anonymous"
        with connect() as conn:
            conn.execute("INSERT INTO responses(respondent_code,answers_json,created_at) VALUES(?,?,?)",
                         (respondent_code, json.dumps(answers), datetime.now().isoformat(timespec="seconds")))
        flash("Survey response saved successfully.", "success")
        return redirect(url_for("survey"))
    return render_template("survey.html", questions=QUESTIONS)

@app.route("/results")
def results():
    if not current_user():
        return redirect(url_for("login"))
    with connect() as conn:
        rows = conn.execute("SELECT answers_json FROM responses ORDER BY id DESC").fetchall()
    results_data = []
    for key, prompt, options in QUESTIONS:
        counts = Counter()
        for row in rows:
            try:
                answer = json.loads(row["answers_json"]).get(key)
                if answer in options:
                    counts[answer] += 1
            except (ValueError, TypeError):
                pass
        results_data.append({"key": key, "prompt": prompt, "options": options,
                             "counts": [counts[o] for o in options],
                             "percentages": [round(counts[o] * 100 / len(rows), 1) if rows else 0 for o in options]})
    return render_template("results.html", results=results_data, total=len(rows))

@app.route("/activities")
def activities():
    with connect() as conn:
        items = conn.execute("SELECT * FROM activities ORDER BY id").fetchall()
    return render_template("activities.html", activities=items)

@app.route("/export.csv")
def export_csv():
    if not current_user():
        return redirect(url_for("login"))
    with connect() as conn:
        rows = conn.execute("SELECT respondent_code,answers_json,created_at FROM responses ORDER BY id").fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Respondent code"] + [q[1] for q in QUESTIONS] + ["Submitted at"])
    for row in rows:
        answers = json.loads(row["answers_json"])
        writer.writerow([row["respondent_code"]] + [answers.get(q[0], "") for q in QUESTIONS] + [row["created_at"]])
    from flask import Response
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=stem_survey_responses.csv"})

if __name__ == "__main__":
    app.run(debug=True)
