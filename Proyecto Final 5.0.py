# Gestor de tareas con calendario interactivo usando Tkinter y SQLite
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import calendar
from datetime import datetime, date

class TaskManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Tareas")
        # Configurar la base de datos
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

        # Variables de fecha actual
        today = date.today()
        self.cur_year = today.year
        self.cur_month = today.month
        self.selected_date = today

        # Configurar la interfaz
        self.setup_ui()
        # Mostrar calendario inicial y tareas
        self.update_calendar()
        self.refresh_tasks()

    def setup_ui(self):
        """Crear los componentes de la interfaz."""
        # Marco para calendario
        cal_frame = tk.Frame(self)
        cal_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Navegación del mes
        nav_frame = tk.Frame(cal_frame)
        nav_frame.pack()
        prev_btn = tk.Button(nav_frame, text="<", width=3, command=self.prev_month)
        prev_btn.grid(row=0, column=0)
        self.month_label = tk.Label(nav_frame, text="", width=15)
        self.month_label.grid(row=0, column=1)
        next_btn = tk.Button(nav_frame, text=">", width=3, command=self.next_month)
        next_btn.grid(row=0, column=2)

        # Días de la semana (Lun a Dom)
        days_frame = tk.Frame(cal_frame)
        days_frame.pack()
        week_days = ["Lun", "Mar", "Mi\u00e9", "Jue", "Vie", "S\u00e1b", "Dom"]
        for i, day in enumerate(week_days):
            tk.Label(days_frame, text=day, width=4).grid(row=0, column=i)

        # Celdas de días
        self.day_btns = []
        for r in range(6):
            row = []
            for c in range(7):
                btn = tk.Button(days_frame, text="", width=4,
                                command=lambda r=r, c=c: self.select_date(r, c))
                btn.grid(row=r+1, column=c)
                row.append(btn)
            self.day_btns.append(row)

        # Marco para lista de tareas
        list_frame = tk.Frame(self)
        list_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        tk.Label(list_frame, text="Tareas para la fecha seleccionada:").pack()
        # Treeview para tareas
        columns = ("Título", "Prioridad", "Etiquetas")
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Botones de acción
        btn_frame = tk.Frame(list_frame)
        btn_frame.pack(pady=5)
        add_btn = tk.Button(btn_frame, text="Agregar Tarea", command=self.add_task)
        add_btn.grid(row=0, column=0, padx=5)
        edit_btn = tk.Button(btn_frame, text="Editar Tarea", command=self.edit_task)
        edit_btn.grid(row=0, column=1, padx=5)
        del_btn = tk.Button(btn_frame, text="Eliminar Tarea", command=self.delete_task)
        del_btn.grid(row=0, column=2, padx=5)

    def update_calendar(self):
        """Actualizar el calendario del mes actual."""
        # Etiqueta de mes y año
        month_name = calendar.month_name[self.cur_month]
        self.month_label.config(text=f"{month_name} {self.cur_year}")

        # Obtener la matriz de días
        cal = calendar.monthcalendar(self.cur_year, self.cur_month)
        # Aplanar semanas a matriz 6x7
        for r in range(6):
            for c in range(7):
                try:
                    day = cal[r][c]
                except IndexError:
                    day = 0
                btn = self.day_btns[r][c]
                if day == 0:
                    btn.config(text="", state=tk.DISABLED, bg="SystemButtonFace")
                else:
                    btn.config(text=str(day), state=tk.NORMAL)
                    # Verificar si hay tareas en esta fecha
                    date_str = f"{self.cur_year}-{self.cur_month:02d}-{day:02d}"
                    self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE due_date=?", (date_str,))
                    has_tasks = self.cursor.fetchone()[0] > 0
                    # Colorear según estado
                    if self.selected_date.year == self.cur_year and \
                       self.selected_date.month == self.cur_month and \
                       self.selected_date.day == day:
                        btn.config(bg="orange")
                    elif has_tasks:
                        btn.config(bg="lightblue")
                    else:
                        btn.config(bg="SystemButtonFace")

    def prev_month(self):
        """Navegar al mes anterior."""
        if self.cur_month == 1:
            self.cur_month = 12
            self.cur_year -= 1
        else:
            self.cur_month -= 1
        # Ajustar selected_date al mes actual
        self.selected_date = date(self.cur_year, self.cur_month, 1)
        self.update_calendar()
        self.refresh_tasks()

    def next_month(self):
        """Navegar al mes siguiente."""
        if self.cur_month == 12:
            self.cur_month = 1
            self.cur_year += 1
        else:
            self.cur_month += 1
        self.selected_date = date(self.cur_year, self.cur_month, 1)
        self.update_calendar()
        self.refresh_tasks()

    def select_date(self, row, col):
        """Seleccionar una fecha del calendario."""
        day = self.day_btns[row][col]['text']
        if day:
            self.selected_date = date(self.cur_year, self.cur_month, int(day))
            self.update_calendar()
            self.refresh_tasks()

    def refresh_tasks(self):
        """Actualizar la lista de tareas para la fecha seleccionada."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        date_str = self.selected_date.strftime("%Y-%m-%d")
        self.cursor.execute("SELECT id, title, priority, tags FROM tasks WHERE due_date=? ORDER BY priority", (date_str,))
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", iid=row[0], values=(row[1], row[2], row[3]))

    def add_task(self):
        """Abrir ventana para agregar una nueva tarea."""
        self.task_window()

    def edit_task(self):
        """Abrir ventana para editar la tarea seleccionada."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una tarea para editar.")
            return
        task_id = int(selected[0])
        # Obtener datos de la tarea
        self.cursor.execute("SELECT title, description, due_date, priority, tags FROM tasks WHERE id=?", (task_id,))
        task = self.cursor.fetchone()
        if task:
            self.task_window(task_id, task)

    def delete_task(self):
        """Eliminar la tarea seleccionada."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una tarea para eliminar.")
            return
        task_id = int(selected[0])
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", "¿Eliminar esta tarea?"):
            self.cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            self.conn.commit()
            self.refresh_tasks()
            self.update_calendar()

    def task_window(self, task_id=None, task=None):
        """Ventana para agregar o editar una tarea."""
        win = tk.Toplevel(self)
        win.grab_set()
        if task_id:
            win.title("Editar Tarea")
        else:
            win.title("Nueva Tarea")

        # Etiquetas y entradas
        tk.Label(win, text="Título:").grid(row=0, column=0, sticky=tk.W, pady=2)
        title_var = tk.StringVar(value=task[0] if task else "")
        tk.Entry(win, textvariable=title_var, width=30).grid(row=0, column=1, pady=2)

        tk.Label(win, text="Descripción:").grid(row=1, column=0, sticky=tk.W, pady=2)
        desc_var = tk.StringVar(value=task[1] if task else "")
        tk.Entry(win, textvariable=desc_var, width=30).grid(row=1, column=1, pady=2)

        tk.Label(win, text="Fecha límite (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W, pady=2)
        date_var = tk.StringVar(value=task[2] if task else self.selected_date.strftime("%Y-%m-%d"))
        tk.Entry(win, textvariable=date_var, width=15).grid(row=2, column=1, pady=2, sticky=tk.W)

        tk.Label(win, text="Prioridad:").grid(row=3, column=0, sticky=tk.W, pady=2)
        prio_var = tk.StringVar(value=task[3] if task else "Media")
        prio_combo = ttk.Combobox(win, textvariable=prio_var, values=["Alta", "Media", "Baja"], width=12)
        prio_combo.grid(row=3, column=1, pady=2, sticky=tk.W)
        prio_combo.state(["readonly"])

        tk.Label(win, text="Etiquetas:").grid(row=4, column=0, sticky=tk.W, pady=2)
        tags_var = tk.StringVar(value=task[4] if task else "")
        tk.Entry(win, textvariable=tags_var, width=30).grid(row=4, column=1, pady=2)

        def save():
            title = title_var.get().strip()
            desc = desc_var.get().strip()
            due = date_var.get().strip()
            prio = prio_var.get()
            tags = tags_var.get().strip()
            if not title:
                messagebox.showwarning("Advertencia", "El título es obligatorio.")
                return
            try:
                # Verificar formato de fecha
                datetime.strptime(due, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Advertencia", "Fecha inválida. Use formato YYYY-MM-DD.")
                return
            if task_id:
                # Actualizar tarea existente
                self.cursor.execute("""UPDATE tasks SET title=?, description=?, due_date=?, priority=?, tags=?
                                       WHERE id=?""", (title, desc, due, prio, tags, task_id))
            else:
                # Insertar nueva tarea
                self.cursor.execute("""INSERT INTO tasks (title, description, due_date, priority, tags)
                                       VALUES (?, ?, ?, ?, ?)""", (title, desc, due, prio, tags))
            self.conn.commit()
            win.destroy()
            self.update_calendar()
            self.refresh_tasks()

        save_btn = tk.Button(win, text="Guardar", command=save)
        save_btn.grid(row=5, column=0, columnspan=2, pady=5)


if __name__ == "__main__":
    app = TaskManagerApp()
    app.mainloop()
