import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required
from sqlite3 import IntegrityError  # or RuntimeError if using CS50 SQL()

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///fintech.db")

@app.context_processor
def inject_user():
    user_id = session.get("user_id")
    if user_id:
        user_row = db.execute("SELECT username FROM users WHERE id = ?", user_id)
        if user_row:
            return {"logged_in_username": user_row[0]["username"]}
    return {"logged_in_username": None}


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods = ["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Check if username was inserted
        if not username:
            render_m = "Enter Username"
            return render_template("apology.html", render_message = render_m)
        # Check if password was inserted
        elif not password:
            render_m = "Enter Password"
            return render_template("apology.html", render_message = render_m)
        # dehash the password
        user_row = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(user_row) != 1 or not check_password_hash( user_row[0]["hash"], password):
            render_m = "Invalid username and/or Password"
            return render_template("apology.html", render_message = render_m)
        # if everthing is ok than it should redirect to homepage

        session["user_id"] = user_row[0]["id"]

        return redirect("/homepage")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

from datetime import datetime

@app.route("/homepage", methods=["GET", "POST"])
@login_required
def index():
    user_id = session["user_id"]

    # Always fetch goal info first
    goal_row = db.execute(
        "SELECT monthly_dream, monthly_current, last_income_update FROM goal WHERE user_id = ?",
        user_id
    )

    if len(goal_row) == 0:
        m_dream = 0.0
        m_current = 0.0
        last_update = None
    else:
        m_dream = goal_row[0]["monthly_dream"]
        m_current = goal_row[0]["monthly_current"]
        last_update = goal_row[0]["last_income_update"]

    # Monthly logic
    current_month = datetime.now().strftime("%Y-%m")
    if not last_update or last_update != current_month:
        current_holdings = db.execute("SELECT holdings FROM users WHERE id = ?", user_id)[0]["holdings"]
        new_balance = current_holdings + m_current

        db.execute("UPDATE users SET holdings = ? WHERE id = ?", new_balance, user_id)
        db.execute("UPDATE goal SET last_income_update = ?, monthly_current = 0 WHERE user_id = ?", current_month, user_id)
        m_current = 0

    if request.method == "POST":
        trade = request.form.get("trade")
        text = request.form.get("text")

        try:
            amount = float(request.form.get("holding"))
        except (ValueError, TypeError):
            return render_template("apology.html", render_message="Invalid amount")

        if not trade or amount <= 0:
            return render_template("apology.html", render_message="Invalid trade or amount")

        user_cash = db.execute("SELECT holdings FROM users WHERE id = ?", user_id)[0]["holdings"]

        if trade == "bought":
            if user_cash < amount:
                return render_template("apology.html", render_message="Insufficient funds")
            new_balance = user_cash - amount
            m_current -= amount  # Deduct from monthly current
        elif trade == "recieved":
            new_balance = user_cash + amount
            m_current += amount  # Add to monthly current
        else:
            return render_template("apology.html", render_message="Invalid trade type")

        db.execute("UPDATE users SET holdings = ? WHERE id = ?", new_balance, user_id)
        db.execute("UPDATE goal SET monthly_current = ? WHERE user_id = ?", m_current, user_id)

        db.execute(
            "INSERT INTO transactions (user_id, trade, amount, text) VALUES (?, ?, ?, ?)",
            user_id, trade, amount, text
        )

        return redirect("/homepage")

    # Calculate progress
    progress_percentage = 0
    achieved = False
    if m_dream > 0:
        progress_percentage = min((m_current / m_dream) * 100, 100)
        achieved = m_current >= m_dream

    user_cash = db.execute("SELECT holdings FROM users WHERE id = ?", user_id)[0]["holdings"]
    recent_transactions = db.execute(
        "SELECT trade, amount, text, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10",
        user_id
    )

    return render_template(
        "index.html",
        bank_balance=user_cash,
        transactions=recent_transactions,
        m_dream=m_dream,
        m_current=m_current,
        progress_percentage=progress_percentage,
        achieved=achieved
    )




@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        rpassword = request.form.get("confirm")
        money = request.form.get("holding")

        if not username:
            return render_template("apology.html", render_message="Forgot username")
        elif not password:
            return render_template("apology.html", render_message="Forgot password")
        elif not rpassword:
            return render_template("apology.html", render_message="Forgot to confirm password")
        elif password != rpassword:
            return render_template("apology.html", render_message="Passwords do not match")
        elif not money:
            return render_template("apology.html", render_message="Enter a number")

        try:
            float_money = float(money)
            if float_money < 0.00:
                return render_template("apology.html", render_message="Enter a positive number")
        except ValueError:
            return render_template("apology.html", render_message="Enter a valid number")

        hash_password = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users (username, hash, holdings) VALUES (?, ?, ?)", username, hash_password, float_money)
        except RuntimeError:
            return render_template("apology.html", render_message="Username is already being used")

        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/goal", methods = ["GET", "POST"])
@login_required
def goal():
    if request.method == "POST":

        user_id = session["user_id"]

        try:
            m_dream = float(request.form.get("monthly_dream"))
            m_current = float(request.form.get("monthly_current"))
        except ValueError:
            return render_template("apology.html", render_message = "Invalid number")

        if m_dream < 0.00 or m_current < 0.00:
            return render_template("apology.html", render_message = "Enter a positive number")


        # Check if a goal already exists for this user
        existing = db.execute("SELECT id FROM goal WHERE user_id = ?", user_id)

        if existing:
            # Update the existing goal
            db.execute(
                "UPDATE goal SET monthly_dream = ?, monthly_current = ? WHERE user_id = ?",
                m_dream, m_current, user_id
            )
        else:
            # Insert a new goal
            db.execute(
                "INSERT INTO goal (user_id, monthly_dream, monthly_current) VALUES (?, ?, ?)",
                user_id, m_dream, m_current
            )


        return redirect("/homepage")

    else:
        return render_template("goal.html")


@app.route("/history")
@login_required
def history():
    user_id = session["user_id"]

    # Get ALL transactions, newest first
    transactions = db.execute(
        "SELECT trade, amount, text, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC",
        user_id
    )

    return render_template("history.html", transactions=transactions)
    l
