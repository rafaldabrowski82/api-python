from flask import Flask, request, jsonify, Response
from ariadne import QueryType, MutationType, make_executable_schema, graphql_sync
from ariadne.explorer import ExplorerGraphiQL
import mysql.connector
import os
import json

# ==========================================
#  FLASK + REST API
# ==========================================

app = Flask(__name__)

# Konfiguracja połączenia z bazą danych (MariaDB / MySQL)
db_config = {
    "host": os.getenv("DB_HOST", "db"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "rootpass"),
    "database": os.getenv("DB_NAME", "rest_demo")
}

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

# CREATE (C)
@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    status = data.get("status")

    if not title or not description or not status:
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s)",
        (title, description, status)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"message": "Task added", "id": new_id}), 201

# READ ALL (R)
@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    ordered_tasks = [order_task(task) for task in tasks]
    return jsonify(ordered_tasks)

# READ ONE (R)
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

    return Response(
        json.dumps(order_task(task), indent=4, sort_keys=False),
        mimetype="application/json"
    )

# UPDATE (U)
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

# DELETE (D)
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Task deleted"})


# ==========================================
#  GRAPHQL (Ariadne)
# ==========================================

type_defs = """
    type Task {
        id: ID!
        title: String!
        description: String!
        status: String!
    }

    type Query {
        allTasks: [Task!]!
        task(id: ID!): Task
    }

    type Mutation {
        createTask(title: String!, description: String!, status: String!): Task!
        updateTask(id: ID!, title: String, description: String, status: String): Task
        deleteTask(id: ID!): Boolean!
    }
"""

query = QueryType()
mutation = MutationType()

# --- RESOLVERY (Query) ---
@query.field("allTasks")
def resolve_all_tasks(*_):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@query.field("task")
def resolve_task(*_, id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE id=%s", (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

# --- RESOLVERY (Mutation) ---
@mutation.field("createTask")
def resolve_create_task(*_, title, description, status):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s)",
        (title, description, status)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM tasks WHERE id=%s", (new_id,))
    new_task = cursor.fetchone()
    cursor.close()
    conn.close()
    return new_task

@mutation.field("updateTask")
def resolve_update_task(*_, id, title=None, description=None, status=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    updates = []
    values = []

    if title:
        updates.append("title=%s")
        values.append(title)
    if description:
        updates.append("description=%s")
        values.append(description)
    if status:
        updates.append("status=%s")
        values.append(status)

    if updates:
        sql = f"UPDATE tasks SET {', '.join(updates)} WHERE id=%s"
        values.append(id)
        cursor.execute(sql, tuple(values))
        conn.commit()

    cursor.execute("SELECT * FROM tasks WHERE id=%s", (id,))
    updated = cursor.fetchone()
    cursor.close()
    conn.close()
    return updated

@mutation.field("deleteTask")
def resolve_delete_task(*_, id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=%s", (id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return deleted

# --- Tworzenie schematu Ariadne ---
schema = make_executable_schema(type_defs, [query, mutation])

@app.route("/graphql", methods=["GET"])
def graphql_explorer():
    return ExplorerGraphiQL().html(None)

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=True)
    status_code = 200 if success else 400
    return jsonify(result), status_code


# ==========================================
#  RUN
# ==========================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)