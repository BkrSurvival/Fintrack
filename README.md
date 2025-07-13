# Fintrack — Financial Tracker

## 📘 Overview

**Fintrack** is a personal financial tracker built with Flask, SQLite, and Bootstrap. It helps users track their income and expenses, set monthly income goals, and visualize progress with a modern and clean interface.

---

## 🔐 Authentication Features

### Register
- Create a new account with a **username**, **password** (with confirmation), and **initial bank balance**.
- Passwords are securely stored.
- Redirects to the login page upon successful registration.

### Login
- Authenticates users using their registered credentials.
- Initiates a user session.
- Displays error messages if credentials are incorrect.

### Logout
- Ends the current session.
- Redirects back to the login page.

---

## ✨ Core Features

### 🏠 Homepage
- Displays your current **bank balance**.
- Allows you to **add transactions**:
  - **Bought** (spending money).
  - **Received** (income).
- Shows the **10 most recent transactions**.
- Includes a **progress circle** that tracks your monthly income goal:
  - If your monthly income meets or exceeds your goal, the circle turns **green** and shows "**Achieved**".
  - The circle resets automatically at the beginning of each month.

### 📜 History
- Lists **all previous transactions** chronologically.

### 🎯 Goal Page
- Allows you to set:
  - Your **monthly dream income** (target).
  - Your **current income this month** (progress).
- Validates entries to ensure they are positive and not empty.
- Progress is visualized on the homepage.

---

## 🧠 Technical Details

- **Backend**: Flask (Python), SQLite
- **Frontend**: HTML, Jinja2 templates, Bootstrap 5
- **Session Management**: Uses Flask session with `@login_required` decorator
- **Database**:
  - `users`: Stores login credentials and current holdings
  - `transactions`: Records all user transactions
  - `goal`: Stores monthly income goals and current progress

---

## 📌 Notes

This project includes a monthly reset feature:
- At the start of a new month, your monthly income progress resets.
- Your balance automatically updates with the income from the previous month.

This app was developed as a personal finance tool and a learning project to improve my backend and frontend skills.

---

## 💡 Future Improvements You can make :D (Optional Ideas)
- Add category tagging for transactions (e.g., food, rent, salary).
- Graphs for spending habits.
- Monthly income/expense history.
- Dark mode.

---

## 📄 License

Bhaskar Survaiya