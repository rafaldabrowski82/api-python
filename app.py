from flask import Flask, request, jsonify
import mysql.connector
import os

# Tworzymy aplikację Flask
# Flask to lekki framework do budowania API
app = Flask(__name__)

# Konfiguracja połączenia z MariaDB
# To jak adres i dane logowania do bazy
db_config = {
    "host": os.getenv("DB_HOST", "db"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "rootpass"),
    "database": os.getenv("DB_NAME", "rest_demo")
}

# Funkcja pomocnicza do otwierania połączenia z bazą danych
def get_db_connection():
    return mysql.connector.connect(**db_config)

#########################
#   R E S T - T A S K S  #
#########################

# CREATE (C) → Dodawanie nowego zadania
@app.route("/tasks", methods=["POST"])
def add_task():
    # Pobieramy dane z requestu jako JSON
    data = request.get_json()
    title = data.get("title")  # Wyciągamy pole 'title'

    conn = get_db_connection()
    cursor = conn.cursor()

    # Wstawiamy nowe zadanie do bazy
    cursor.execute("INSERT INTO tasks (title) VALUES (%s)", (title,))
    conn.commit()

    # Pobieramy ID nowego wpisu
    new_id = cursor.lastrowid

    cursor.close()
    conn.close()

    # Zwracamy odpowiedź 201 (Created)
    return jsonify({"message": "Task added", "id": new_id}), 201

# READ ALL (R) → Pobranie wszystkich zadań
@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # dictionary=True → zwróć w formie JSON

    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(tasks)

# READ ONE (R) → Pobranie konkretnego zadania
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()

    cursor.close()
    conn.close()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task)

# UPDATE (U) → Aktualizacja zadania
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    new_title = data.get("title")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Aktualizujemy rekord
    cursor.execute("UPDATE tasks SET title=%s WHERE id=%s", (new_title, task_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Task updated"})

# DELETE (D) → Usuwanie zadania
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Task deleted"})

# Uruchamiamy serwer Flask
# debug=True → automatycznie przeładowuje przy zmianach
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

