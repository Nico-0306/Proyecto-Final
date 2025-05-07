import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime


class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Tareas Simplificado")
        self.root.geometry("900x600")
        
        # Variables principales
        self.tasks = []
        self.current_task = None
        
        # Crear interfaz
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo (formulario)
        left_panel = ttk.Frame(main_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Panel derecho (lista y calendario)
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Formulario de tareas
        self.create_task_form(left_panel)
        
        # Lista de tareas
        self.create_task_list(right_panel)
        
        # Calendario
        self.create_calendar(right_panel)
    
    def create_task_form(self, parent):
        form_frame = ttk.LabelFrame(parent, text="Nueva Tarea", padding=10)
        form_frame.pack(fill=tk.X, pady=5)
        
        # Campos del formulario
        fields = [
            ("Título:", "title", tk.StringVar()),
            ("Descripción:", "desc", tk.StringVar()),
            ("Fecha límite:", "due_date", tk.StringVar()),
            ("Prioridad:", "priority", tk.StringVar(value="media")),
            ("Estado:", "status", tk.StringVar(value="pendiente")),
            ("Etiquetas:", "tags", tk.StringVar())
        ]
        
        self.form_vars = {name: var for (label, name, var) in fields}
        
        for row, (label, name, var) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)
            
            if name == "priority":
                ttk.Combobox(form_frame, textvariable=var, 
                            values=["alta", "media", "baja"], width=18).grid(row=row, column=1, pady=2)
            elif name == "status":
                ttk.Combobox(form_frame, textvariable=var, 
                            values=["pendiente", "en progreso", "completada"], width=18).grid(row=row, column=1, pady=2)
            elif name == "due_date":
                entry = ttk.Entry(form_frame, textvariable=var, width=20)
                entry.grid(row=row, column=1, pady=2)
                ttk.Button(form_frame, text="📅", width=3, 
                          command=self.show_calendar).grid(row=row, column=2, padx=2)
            else:
                ttk.Entry(form_frame, textvariable=var, width=22).grid(row=row, column=1, pady=2)
        
        # Botones
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(fields)+1, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="Guardar", command=self.save_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self.clear_form).pack(side=tk.LEFT, padx=5)
    
    def create_task_list(self, parent):
        list_frame = ttk.LabelFrame(parent, text="Lista de Tareas", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview para mostrar tareas
        self.task_tree = ttk.Treeview(list_frame, columns=("title", "due_date", "priority", "status"), show="headings")
        self.task_tree.heading("title", text="Título")
        self.task_tree.heading("due_date", text="Fecha")
        self.task_tree.heading("priority", text="Prioridad")
        self.task_tree.heading("status", text="Estado")
        
        self.task_tree.column("title", width=200)
        self.task_tree.column("due_date", width=100)
        self.task_tree.column("priority", width=80)
        self.task_tree.column("status", width=100)
        
        self.task_tree.pack(fill=tk.BOTH, expand=True)
        
        # Barra de desplazamiento
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de acción
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Editar", command=self.edit_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_task).pack(side=tk.LEFT, padx=5)
    
    def create_calendar(self, parent):
        cal_frame = ttk.LabelFrame(parent, text="Calendario", padding=10)
        cal_frame.pack(fill=tk.BOTH, pady=5)
        
        self.calendar = Calendar(cal_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack(fill=tk.BOTH)
        
        ttk.Button(cal_frame, text="Ver tareas en calendario", 
                  command=self.show_tasks_in_calendar).pack(pady=5)
    
    def show_calendar(self):
        def set_date():
            self.form_vars["due_date"].set(cal.get_date())
            top.destroy()
        
        top = tk.Toplevel(self.root)
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10)
        ttk.Button(top, text="Seleccionar", command=set_date).pack(pady=5)
    
    def save_task(self):
        # Validación básica
        if not self.form_vars["title"].get():
            messagebox.showerror("Error", "El título es obligatorio")
            return
            
        task = {
            "title": self.form_vars["title"].get(),
            "description": self.form_vars["desc"].get(),
            "due_date": self.form_vars["due_date"].get() or "Sin fecha",
            "priority": self.form_vars["priority"].get(),
            "status": self.form_vars["status"].get(),
            "tags": [tag.strip() for tag in self.form_vars["tags"].get().split(",") if tag.strip()]
        }
        
        if self.current_task is None:
            # Nueva tarea
            self.tasks.append(task)
            messagebox.showinfo("Éxito", "Tarea agregada correctamente")
        else:
            # Editar tarea existente
            index = self.tasks.index(self.current_task)
            self.tasks[index] = task
            messagebox.showinfo("Éxito", "Tarea actualizada correctamente")
            self.current_task = None
        
        self.update_task_list()
        self.clear_form()
    
    def clear_form(self):
        for var in self.form_vars.values():
            var.set("")
        self.form_vars["priority"].set("media")
        self.form_vars["status"].set("pendiente")
        self.current_task = None
    
    def update_task_list(self):
        # Limpiar lista
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Agregar tareas
        for task in self.tasks:
            self.task_tree.insert("", tk.END, values=(
                task["title"],
                task["due_date"],
                task["priority"],
                task["status"]
            ))
    
    def edit_task(self):
        selected = self.task_tree.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una tarea para editar")
            return
            
        item = self.task_tree.item(selected)
        task_title = item["values"][0]
        
        # Buscar la tarea completa
        for task in self.tasks:
            if task["title"] == task_title:
                self.current_task = task
                break
        
        # Llenar el formulario
        if self.current_task:
            self.form_vars["title"].set(self.current_task["title"])
            self.form_vars["desc"].set(self.current_task["description"])
            self.form_vars["due_date"].set(self.current_task["due_date"])
            self.form_vars["priority"].set(self.current_task["priority"])
            self.form_vars["status"].set(self.current_task["status"])
            self.form_vars["tags"].set(", ".join(self.current_task["tags"]))
    
    def delete_task(self):
        selected = self.task_tree.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una tarea para eliminar")
            return
            
        item = self.task_tree.item(selected)
        task_title = item["values"][0]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar la tarea '{task_title}'?"):
            for task in self.tasks:
                if task["title"] == task_title:
                    self.tasks.remove(task)
                    break
            
            self.update_task_list()
            messagebox.showinfo("Éxito", "Tarea eliminada correctamente")
    
    def show_tasks_in_calendar(self):
        # Limpiar eventos anteriores
        for event in self.calendar.calevent_get():
            self.calendar.calevent_remove(event)
        
        # Agregar tareas al calendario
        for task in self.tasks:
            if task["due_date"] and task["due_date"] != "Sin fecha":
                try:
                    self.calendar.calevent_create(
                        datetime.strptime(task["due_date"], '%Y-%m-%d'),
                        task["title"],
                        f"Prioridad: {task['priority']}"
                    )
                except ValueError:
                    continue

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()