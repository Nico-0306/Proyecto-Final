# Borrador - Ventana emergente para agregar una tarea (reutilizable)
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

class FormularioTarea(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Agregar tarea")
        self.conn = sqlite3.connect("tasks.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                title TEXT,
                                description TEXT,
                                due_date TEXT,
                                priority TEXT,
                                tags TEXT)""")
        self.conn.commit()

        tk.Label(self, text="Título:").grid(row=0, column=0)
        self.title_var = tk.StringVar()
        tk.Entry(self, textvariable=self.title_var).grid(row=0, column=1)

        tk.Label(self, text="Fecha (YYYY-MM-DD):").grid(row=1, column=0)
        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        tk.Entry(self, textvariable=self.date_var).grid(row=1, column=1)

        tk.Label(self, text="Prioridad:").grid(row=2, column=0)
        self.prio_var = tk.StringVar(value="Media")
        ttk.Combobox(self, textvariable=self.prio_var, values=["Alta", "Media", "Baja"]).grid(row=2, column=1)

        tk.Button(self, text="Guardar", command=self.save_task).grid(row=3, columnspan=2, pady=5)

    def save_task(self):
        try:
            datetime.strptime(self.date_var.get(), "%Y-%m-%d")
        except:
            messagebox.showerror("Error", "Formato de fecha incorrecto")
            return

        self.cursor.execute("INSERT INTO tasks (title, due_date, priority) VALUES (?, ?, ?)",
                            (self.title_var.get(), self.date_var.get(), self.prio_var.get()))
        self.conn.commit()
        messagebox.showinfo("Éxito", "Tarea guardada.")
        self.destroy()

if __name__ == "__main__":
    app = FormularioTarea()
    app.mainloop()
