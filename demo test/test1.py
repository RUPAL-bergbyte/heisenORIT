import sqlite3
import os

SECRET_KEY = "supersecret123"
DB_PASSWORD = "admin1234"

def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()

def login(username, password):
    user = get_user(username)
    if user and user[2] == password:
        return True
    return False

def read_file(filename):
    path = "/var/data/" + filename
    return open(path).read()

def run_report(report_name):
    os.system("python reports/" + report_name)