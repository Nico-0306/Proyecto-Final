#Nueva base de datos para guardar o recuperar tareas

import sqlite3
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_name="tasks.db"):
        self.db_name = db_name
        self._create_tables()

    @contextmanager
    def _get_cursor(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        finally:
            conn.close()

    def _create_tables(self):
        with self._get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT,
                    priority TEXT CHECK(priority IN ('alta', 'media', 'baja')),
                    status TEXT CHECK(status IN ('pendiente', 'en progreso', 'completada')),
                    tags TEXT
                )
            """)

    def add_task(self, task):
        with self._get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO tasks (title, description, due_date, priority, status, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                task['title'],
                task['description'],
                task['due_date'],
                task['priority'],
                task['status'],
                ",".join(task['tags']) if task['tags'] else ""
            ))

    def get_all_tasks(self):
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM tasks")
            rows = cursor.fetchall()
            return [{
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'due_date': row[3],
                'priority': row[4],
                'status': row[5],
                'tags': row[6].split(",") if row[6] else []
            } for row in rows]

