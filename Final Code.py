import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import Calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from contextlib import contextmanager

# ======================
# BASE DE DATOS (SQLite)
# ======================
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
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority ON tasks(priority)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)")

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
            return cursor.lastrowid

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

    def update_task(self, task_id, updated_task):
        with self._get_cursor() as cursor:
            cursor.execute("""
                UPDATE tasks 
                SET title=?, description=?, due_date=?, priority=?, status=?, tags=?
                WHERE id=?
            """, (
                updated_task['title'],
                updated_task['description'],
                updated_task['due_date'],
                updated_task['priority'],
                updated_task['status'],
                ",".join(updated_task['tags']) if updated_task['tags'] else "",
                task_id
            ))

    def delete_task(self, task_id):
        with self._get_cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))

# ======================
# INTERFAZ GRÁFICA
# ======================
class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Tareas Avanzado")
        self.root.geometry("1200x700")
        self.root.configure(bg='#2d2d2d')  # Fondo oscuro
        
        # Configuración de estilos
        self._setup_styles()
        
        # Base de datos
        self.db = DatabaseManager()
        self.tasks = self.db.get_all_tasks()
        self.filtered_tasks = []
        
        # Variables para filtros
        self.filter_priority = tk.StringVar(value="Todas")
        self.filter_status = tk.StringVar(value="Todas")
        self.filter_tags = tk.StringVar(value="")
        
        # Variables para nueva tarea
        self.new_task_title = tk.StringVar()
        self.new_task_desc = tk.StringVar()
        self.new_task_due_date = tk.StringVar()
        self.new_task_priority = tk.StringVar(value="media")
        self.new_task_status = tk.StringVar(value="pendiente")
        self.new_task_tags = tk.StringVar()
        
        # Crear widgets
        self.create_widgets()
    
    def _setup_styles(self):
        """Configura los estilos visuales de la aplicación"""
        style = ttk.Style()
        
        # Tema general
        style.theme_use('clam')
        
        # Colores
        bg_color = '#2d2d2d'
        fg_color = '#ffffff'
        accent_color = '#3c6e71'
        secondary_color = '#284b63'
        danger_color = '#e63946'
        
        # Configuraciones generales
        style.configure('.', background=bg_color, foreground=fg_color, font=('Arial', 10))
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TButton', background=secondary_color, foreground=fg_color, borderwidth=1)
        style.configure('TEntry', fieldbackground='#3d3d3d', foreground=fg_color)
        style.configure('TCombobox', fieldbackground='#3d3d3d', foreground=fg_color)
        
        # Estilos especiales
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground=accent_color)
        style.configure('Accent.TButton', background=accent_color, foreground=fg_color)
        style.configure('Danger.TButton', background=danger_color, foreground=fg_color)
        
        # Treeview (tabla)
        style.configure('Treeview', 
                       background='#3d3d3d', 
                       foreground=fg_color,
                       fieldbackground='#3d3d3d',
                       rowheight=25)
        style.map('Treeview', background=[('selected', secondary_color)])
        
        style.configure('Treeview.Heading', 
                       background=secondary_color, 
                       foreground=fg_color,
                       relief='flat')
        style.map('Treeview.Heading', background=[('active', accent_color)])

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo (formulario y filtros)
        left_panel = ttk.Frame(main_frame, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Panel derecho (lista de tareas y calendario)
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # ---------------------------
        # Panel izquierdo - Formulario
        # ---------------------------
        form_frame = ttk.LabelFrame(left_panel, text="Nueva Tarea", padding=10)
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_frame, text="Título:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(form_frame, textvariable=self.new_task_title, width=30).grid(row=0, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Descripción:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(form_frame, textvariable=self.new_task_desc, width=30).grid(row=1, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Fecha límite:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(form_frame, textvariable=self.new_task_due_date, width=30).grid(row=2, column=1, pady=2, padx=5)
        ttk.Button(form_frame, text="Seleccionar fecha", command=self.select_date).grid(row=2, column=2, padx=5)
        
        ttk.Label(form_frame, text="Prioridad:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Combobox(form_frame, textvariable=self.new_task_priority, 
                    values=["alta", "media", "baja"], width=27).grid(row=3, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Estado:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Combobox(form_frame, textvariable=self.new_task_status, 
                    values=["pendiente", "en progreso", "completada"], width=27).grid(row=4, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Etiquetas (separadas por comas):").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Entry(form_frame, textvariable=self.new_task_tags, width=30).grid(row=5, column=1, pady=2, padx=5)
        
        ttk.Button(form_frame, text="Agregar Tarea", command=self.add_task, style='Accent.TButton').grid(row=6, column=1, pady=10)
        
        # ---------------------------
        # Panel izquierdo - Filtros
        # ---------------------------
        filter_frame = ttk.LabelFrame(left_panel, text="Filtros", padding=10)
        filter_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(filter_frame, text="Prioridad:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Combobox(filter_frame, textvariable=self.filter_priority, 
                    values=["Todas", "alta", "media", "baja"], width=15).grid(row=0, column=1, pady=2, padx=5)
        
        ttk.Label(filter_frame, text="Estado:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Combobox(filter_frame, textvariable=self.filter_status, 
                    values=["Todas", "pendiente", "en progreso", "completada"], width=15).grid(row=1, column=1, pady=2, padx=5)
        
        ttk.Label(filter_frame, text="Etiquetas:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(filter_frame, textvariable=self.filter_tags, width=15).grid(row=2, column=1, pady=2, padx=5)
        
        ttk.Button(filter_frame, text="Aplicar Filtros", command=self.apply_filters, style='Accent.TButton').grid(row=3, column=1, pady=10)
        
        # ---------------------------
        # Panel derecho - Lista de tareas
        # ---------------------------
        tasks_frame = ttk.LabelFrame(right_panel, text="Lista de Tareas", padding=10)
        tasks_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para mostrar las tareas
        self.tasks_tree = ttk.Treeview(tasks_frame, columns=("title", "due_date", "priority", "status", "tags"), show="headings")
        self.tasks_tree.heading("title", text="Título")
        self.tasks_tree.heading("due_date", text="Fecha Límite")
        self.tasks_tree.heading("priority", text="Prioridad")
        self.tasks_tree.heading("status", text="Estado")
        self.tasks_tree.heading("tags", text="Etiquetas")
        
        self.tasks_tree.column("title", width=200)
        self.tasks_tree.column("due_date", width=100)
        self.tasks_tree.column("priority", width=80)
        self.tasks_tree.column("status", width=100)
        self.tasks_tree.column("tags", width=150)
        
        self.tasks_tree.pack(fill=tk.BOTH, expand=True)
        
        # Barra de desplazamiento
        scrollbar = ttk.Scrollbar(tasks_frame, orient=tk.VERTICAL, command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones para editar/eliminar
        button_frame = ttk.Frame(tasks_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(button_frame, text="Editar", command=self.edit_task, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_task, style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Ver Detalles", command=self.view_details).pack(side=tk.LEFT, padx=5)
        
        # ---------------------------
        # Panel derecho - Calendario
        # ---------------------------
        calendar_frame = ttk.LabelFrame(right_panel, text="Calendario", padding=10)
        calendar_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Calendario interactivo
        self.calendar = Calendar(calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd',
                               background='#3d3d3d', foreground='white', headersbackground='#284b63',
                               normalbackground='#3d3d3d', weekendbackground='#4d4d4d')
        self.calendar.pack(fill=tk.BOTH, expand=True)
        
        # Visualización de tareas en el calendario
        ttk.Button(calendar_frame, text="Mostrar Tareas en Calendario", 
                  command=self.show_calendar_tasks, style='Accent.TButton').pack(pady=5)
        
        # Gráfico de tareas pendientes
        self.create_timeline_chart(right_panel)
        
        # Cargar datos iniciales
        self.apply_filters()
    
    def create_timeline_chart(self, parent):
        chart_frame = ttk.LabelFrame(parent, text="Línea de Tiempo de Tareas", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(8, 3), facecolor='#2d2d2d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(chart_frame, text="Actualizar Gráfico", 
                  command=self.update_timeline_chart, style='Accent.TButton').pack(pady=5)
    
    def update_timeline_chart(self):
        self.ax.clear()
        
        if not self.filtered_tasks:
            self.ax.text(0.5, 0.5, 'No hay tareas para mostrar', 
                        ha='center', va='center', fontsize=12, color='white')
            self.canvas.draw()
            return
        
        # Preparar datos para el gráfico
        tasks = sorted(self.filtered_tasks, key=lambda x: x['due_date'])
        titles = [task['title'] for task in tasks]
        dates = [datetime.strptime(task['due_date'], '%Y-%m-%d') for task in tasks if task['due_date'] != "Sin fecha"]
        priorities = [task['priority'] for task in tasks if task['due_date'] != "Sin fecha"]
        
        # Colores según prioridad
        colors = {'alta': '#e63946', 'media': '#ffbe0b', 'baja': '#2a9d8f'}
        
        # Crear líneas de tiempo
        for i, (title, date, priority) in enumerate(zip(titles, dates, priorities)):
            self.ax.plot([date, date], [i-0.4, i+0.4], color=colors[priority], linewidth=3)
            self.ax.text(date + timedelta(days=1), i, title, va='center', color='white')
        
        # Configurar el gráfico
        self.ax.set_yticks(range(len(tasks)))
        self.ax.set_yticklabels(titles)
        self.ax.set_xlim(min(dates) - timedelta(days=2), max(dates) + timedelta(days=5))
        self.ax.grid(True, color='#4d4d4d')
        self.ax.set_facecolor('#2d2d2d')
        
        # Rotar etiquetas de fecha
        for label in self.ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha('right')
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def select_date(self):
        def set_date():
            self.new_task_due_date.set(cal.get_date())
            top.destroy()
        
        top = tk.Toplevel(self.root)
        top.configure(bg='#2d2d2d')
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd',
                      background='#3d3d3d', foreground='white', headersbackground='#284b63')
        cal.pack(padx=10, pady=10)
        ttk.Button(top, text="Seleccionar", command=set_date, style='Accent.TButton').pack(pady=5)
    
    def add_task(self):
        title = self.new_task_title.get()
        due_date = self.new_task_due_date.get()
        
        if not title:
            messagebox.showerror("Error", "El título es obligatorio")
            return
        
        if due_date and due_date != "Sin fecha":
            try:
                task_date = datetime.strptime(due_date, '%Y-%m-%d')
                if task_date < datetime.now():
                    messagebox.showerror("Error", "La fecha no puede ser en el pasado")
                    return
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                return
        
        task = {
            'title': title,
            'description': self.new_task_desc.get(),
            'due_date': due_date if due_date else "Sin fecha",
            'priority': self.new_task_priority.get(),
            'status': self.new_task_status.get(),
            'tags': [tag.strip() for tag in self.new_task_tags.get().split(",") if tag.strip()]
        }
        
        self.db.add_task(task)
        self.tasks = self.db.get_all_tasks()
        self.apply_filters()
        self.clear_form()
        messagebox.showinfo("Éxito", "Tarea agregada correctamente")
    
    def clear_form(self):
        self.new_task_title.set("")
        self.new_task_desc.set("")
        self.new_task_due_date.set("")
        self.new_task_priority.set("media")
        self.new_task_status.set("pendiente")
        self.new_task_tags.set("")
    
    def apply_filters(self):
        priority_filter = self.filter_priority.get()
        status_filter = self.filter_status.get()
        tags_filter = self.filter_tags.get().lower()
        
        self.filtered_tasks = []
        
        for task in self.tasks:
            # Filtrar por prioridad
            if priority_filter != "Todas" and task['priority'] != priority_filter:
                continue
                
            # Filtrar por estado
            if status_filter != "Todas" and task['status'] != status_filter:
                continue
                
            # Filtrar por etiquetas
            if tags_filter:
                task_tags = [tag.lower() for tag in (task.get('tags', []) or [])]
                search_tags = [tag.strip().lower() for tag in tags_filter.split(",") if tag.strip()]
                
                if not all(any(st in tt for st in search_tags) for tt in task_tags):
                    continue
            
            self.filtered_tasks.append(task)
        
        self.update_tasks_list()
        self.update_timeline_chart()
    
    def update_tasks_list(self):
        # Limpiar el treeview
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
        
        # Agregar las tareas filtradas
        for task in self.filtered_tasks:
            tags = ", ".join(task['tags']) if task['tags'] else ""
            self.tasks_tree.insert("", tk.END, values=(
                task['title'],
                task['due_date'],
                task['priority'],
                task['status'],
                tags
            ))
    
    def get_selected_task(self):
        selected_item = self.tasks_tree.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor seleccione una tarea")
            return None
        
        item_data = self.tasks_tree.item(selected_item)
        task_title = item_data['values'][0]
        
        # Buscar la tarea completa en la lista
        for task in self.tasks:
            if task['title'] == task_title:
                return task, selected_item
        
        return None
    
    def edit_task(self):
        selected = self.get_selected_task()
        if not selected:
            return
        
        task, item_id = selected
        
        def save_changes():
            # Validar título
            new_title = edit_title.get()
            if not new_title:
                messagebox.showerror("Error", "El título es obligatorio")
                return
            
            # Validar fecha
            new_date = edit_due_date.get()
            if new_date and new_date != "Sin fecha":
                try:
                    task_date = datetime.strptime(new_date, '%Y-%m-%d')
                    if task_date < datetime.now():
                        messagebox.showerror("Error", "La fecha no puede ser en el pasado")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                    return
            
            # Actualizar la tarea
            updated_task = {
                'title': new_title,
                'description': edit_desc.get(),
                'due_date': new_date if new_date else "Sin fecha",
                'priority': edit_priority.get(),
                'status': edit_status.get(),
                'tags': [tag.strip() for tag in edit_tags.get().split(",") if tag.strip()]
            }
            
            self.db.update_task(task['id'], updated_task)
            self.tasks = self.db.get_all_tasks()
            self.apply_filters()
            edit_window.destroy()
            messagebox.showinfo("Éxito", "Tarea actualizada correctamente")
        
        # Crear ventana de edición
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Tarea")
        edit_window.configure(bg='#2d2d2d')
        
        # Variables para el formulario de edición
        edit_title = tk.StringVar(value=task['title'])
        edit_desc = tk.StringVar(value=task['description'])
        edit_due_date = tk.StringVar(value=task['due_date'])
        edit_priority = tk.StringVar(value=task['priority'])
        edit_status = tk.StringVar(value=task['status'])
        edit_tags = tk.StringVar(value=", ".join(task['tags']))
        
        # Formulario de edición
        ttk.Label(edit_window, text="Título:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(edit_window, textvariable=edit_title, width=30).grid(row=0, column=1, pady=2, padx=5)
        
        ttk.Label(edit_window, text="Descripción:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(edit_window, textvariable=edit_desc, width=30).grid(row=1, column=1, pady=2, padx=5)
        
        ttk.Label(edit_window, text="Fecha límite:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(edit_window, textvariable=edit_due_date, width=30).grid(row=2, column=1, pady=2, padx=5)
        
        ttk.Label(edit_window, text="Prioridad:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Combobox(edit_window, textvariable=edit_priority, 
                     values=["alta", "media", "baja"], width=27).grid(row=3, column=1, pady=2, padx=5)
        
        ttk.Label(edit_window, text="Estado:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Combobox(edit_window, textvariable=edit_status, 
                     values=["pendiente", "en progreso", "completada"], width=27).grid(row=4, column=1, pady=2, padx=5)
        
        ttk.Label(edit_window, text="Etiquetas (separadas por comas):").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Entry(edit_window, textvariable=edit_tags, width=30).grid(row=5, column=1, pady=2, padx=5)
        
        ttk.Button(edit_window, text="Guardar Cambios", command=save_changes, style='Accent.TButton').grid(row=6, column=1, pady=10)
    
    def delete_task(self):
        selected = self.get_selected_task()
        if not selected:
            return
        
        task, item_id = selected
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro que desea eliminar la tarea '{task['title']}'?"):
            self.db.delete_task(task['id'])
            self.tasks = self.db.get_all_tasks()
            self.apply_filters()
            messagebox.showinfo("Éxito", "Tarea eliminada correctamente")
    
    def view_details(self):
        selected = self.get_selected_task()
        if not selected:
            return
        
        task, item_id = selected
        
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Detalles: {task['title']}")
        details_window.configure(bg='#2d2d2d')
        
        # Mostrar detalles completos
        ttk.Label(details_window, text=f"Título: {task['title']}", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(10, 2), padx=10)
        ttk.Label(details_window, text=f"Descripción: {task['description']}").pack(anchor=tk.W, pady=2, padx=10)
        ttk.Label(details_window, text=f"Fecha límite: {task['due_date']}").pack(anchor=tk.W, pady=2, padx=10)
        ttk.Label(details_window, text=f"Prioridad: {task['priority']}").pack(anchor=tk.W, pady=2, padx=10)
        ttk.Label(details_window, text=f"Estado: {task['status']}").pack(anchor=tk.W, pady=2, padx=10)
        ttk.Label(details_window, text=f"Etiquetas: {', '.join(task['tags']) if task['tags'] else 'Ninguna'}").pack(anchor=tk.W, pady=2, padx=10)
    
    def show_calendar_tasks(self):
        # Crear ventana para mostrar tareas en el calendario
        calendar_window = tk.Toplevel(self.root)
        calendar_window.title("Tareas en Calendario")
        calendar_window.geometry("800x600")
        calendar_window.configure(bg='#2d2d2d')
        
        # Calendario grande
        big_calendar = Calendar(calendar_window, selectmode='day', date_pattern='yyyy-mm-dd',
                              background='#3d3d3d', foreground='white', headersbackground='#284b63')
        big_calendar.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Mostrar tareas en fechas correspondientes
        for task in self.filtered_tasks:
            if task['due_date'] and task['due_date'] != "Sin fecha":
                try:
                    big_calendar.calevent_create(
                        datetime.strptime(task['due_date'], '%Y-%m-%d'),
                        task['title'],
                        f"Prioridad: {task['priority']}, Estado: {task['status']}"
                    )
                except ValueError:
                    continue
        
        # Configurar colores según prioridad
        tag_colors = {'alta': '#e63946', 'media': '#ffbe0b', 'baja': '#2a9d8f'}
        for priority, color in tag_colors.items():
            big_calendar.tag_config(priority, background=color)
        
        # Asignar tags según prioridad
        for event in big_calendar.calevent_get():
            for task in self.filtered_tasks:
                if task['title'] == big_calendar.calevent_cget(event, 'text'):
                    big_calendar.calevent_cget(event, 'tags', task['priority'])
                    break

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()