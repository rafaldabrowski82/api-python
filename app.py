from flask import Flask, request, jsonify, Response
import json
import mysql.connector
import os

# Tworzymy aplikację Flask
app = Flask(__name__)

# Konfiguracja połączenia z bazą danych (MariaDB / MySQL)
db_config = {
    "host": os.getenv("DB_HOST", "db"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "rootpass"),
    "database": os.getenv("DB_NAME", "rest_demo")
}

# Funkcja pomocnicza do otwierania połączenia z bazą danych
def get_db_connection():
    return mysql.connector.connect(**db_config)

# 🔹 Funkcja porządkująca pola w odpowiedzi JSON
def order_task(task):
    """Zwraca słownik pól w ustalonej kolejności"""
    return {
        "id": task["id"],
        "title": task["title"],
        "description": task["description"],
        "status": task["status"]
    }

#########################
#   R E S T - T A S K S  #
#########################

# CREATE (C) → Dodawanie nowego zadania
@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    status = data.get("status")

    # Walidacja danych
    if not title or not description or not status:
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Poprawione zapytanie z 3 placeholderami
    cursor.execute(
        "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s)",
        (title, description, status)
    )
    conn.commit()

    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"message": "Task added", "id": new_id}), 201

# READ ALL (R) → Pobranie wszystkich zadań
@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()

    # 🔹 Zwracamy listę z uporządkowanymi polami
    ordered_tasks = [order_task(task) for task in tasks]
    return jsonify(ordered_tasks)

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

    # 🔹 Zwracamy uporządkowane pola
    return Response(
        json.dumps(order_task(task), indent=4, sort_keys=False),
        mimetype="application/json"
    )

# UPDATE (U) → Aktualizacja zadania
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    new_title = data.get("title")

    if not new_title:
        return jsonify({"error": "Missing field: title"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
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

# Uruchomienie aplikacji
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
