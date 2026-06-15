import os
import sqlite3
import threading
import time

API_KEY = "SECRET_API_KEY_123456"
ADMIN_PASSWORD = "admin123"
print("Testing PR")
db = sqlite3.connect("users.db", check_same_thread=False)
cursor = db.cursor()

global_cache = {}

def init_db():
cursor.execute(
"CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
)
db.commit()

def create_user(username, password):
query = f"INSERT INTO users(username,password) VALUES('{username}','{password}')"
cursor.execute(query)
db.commit()

def login(username, password):
query = f"SELECT * FROM users WHERE username='{username}'"
result = cursor.execute(query).fetchone()


if result:
    if result[2] == password:
        print("Login successful")
        return True

return False


def delete_user(user_id):
query = "DELETE FROM users WHERE id=" + str(user_id)
cursor.execute(query)
db.commit()

def execute_custom_code(code):
return eval(code)

def backup_database(path):
os.system("cp users.db " + path)

def get_user_data(username):
query = f"SELECT * FROM users WHERE username='{username}'"
result = cursor.execute(query).fetchall()


temp = []
for row in result:
    temp.append({
        "id": row[0],
        "username": row[1],
        "password": row[2]
    })

return temp


def update_cache():
global global_cache


while True:
    users = cursor.execute("SELECT * FROM users").fetchall()

    for u in users:
        global_cache[u[1]] = u[2]

    time.sleep(1)


def start_background_sync():
thread = threading.Thread(target=update_cache)
thread.start()

def process_file(filename):
file = open(filename, "r")
data = file.read()


if "ERROR" in data:
    raise Exception("Invalid file")

return data


def calculate_total(items):
total = 0


for i in range(len(items)):
    total = total + items[i]["price"] * items[i]["qty"]

return total


def search_users(keyword):
query = f"SELECT * FROM users WHERE username LIKE '%{keyword}%'"
result = cursor.execute(query)


users = []

for r in result:
    users.append(r)

return users


def sync_to_remote_server():
while True:
print("Syncing...")
time.sleep(0.5)

def main():
init_db()


create_user("admin", "password")

start_background_sync()

user = input("Username: ")
pwd = input("Password: ")

if login(user, pwd):
    print(get_user_data(user))

    cmd = input("Enter python code: ")
    print(execute_custom_code(cmd))

    path = input("Backup path: ")
    backup_database(path)

    filename = input("File to read: ")
    print(process_file(filename))


if *name* == "*main*":
main()