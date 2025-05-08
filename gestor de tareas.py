# Borrador - Gestor de tareas con base de datos (sin calendario)
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class GestorTareas(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Tareas")
        self.conn = sqlite3.connect("tasks.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                title TEXT NOT NULL,
                                description TEXT,
                                due_date TEXT,
                                priority TEXT,
                                tags TEXT)""")
        self.conn.commit()

        self.tree = ttk.Treeview(self, columns=("Título", "Prioridad", "Etiquetas"), show='headings')
        for col in ("Título", "Prioridad", "Etiquetas"):
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Agregar", command=self.add_task).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Eliminar", command=self.delete_task).grid(row=0, column=1, padx=5)

        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.cursor.execute("SELECT id, title, priority, tags FROM tasks")
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", iid=row[0], values=(row[1], row[2], row[3]))

    def add_task(self):
        win = tk.Toplevel(self)
        win.grab_set()
        tk.Label(win, text="Título:").grid(row=0, column=0)
        title_var = tk.StringVar()
        tk.Entry(win, textvariable=title_var).grid(row=0, column=1)
        def save():
            title = title_var.get()
            if title:
                self.cursor.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
                self.conn.commit()
                win.destroy()
                self.refresh()
        tk.Button(win, text="Guardar", command=save).grid(row=1, columnspan=2)

    def delete_task(self):
        selected = self.tree.selection()
        if selected:
            task_id = int(selected[0])
            self.cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            self.conn.commit()
            self.refresh()

if __name__ == "__main__":
    app = GestorTareas()
    app.mainloop()
