import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import Calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TaskManager:
  def__init__(self, root):
  self.root = root
  self.root.title("Gestor de Tareas con Cronograma Interactivo")
  self.root.geometry("1200x700")

#Estructura para almacenar las tareas
self.task = []
self.filtered_tasks = []

#Variables para filtros
self.filter_priority = tk.StringVar(value="Todas")
self.filter_status = tk.StringVar(value="Todas")
self.filter_tags = tk.StringVar(value="")

#Variables para nueva tarea
self.new_task_title = tk.StringVar()
self.new_task_desc = tk.StringVar()
self.new_task_due_date = tk.StringVar()
self.new_task_priority = tk.StringVar(value="media")
self.new_task_status = tk.StringVar(value="pendiente")
self.new_task_tags = tk.StringVar()

# Configurar el estilo
self.style = ttk.Style()
self.style.configure('TFrame', background='#f0f0f0')
self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
self.style.configure('TButton', font=('Arial', 10))
self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))

# Crear widgets
self.creat_widgets()

def create_widgets(self):
  # Frame principal
  main_frame = ttk.Frame(self.root)
  main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Panel izquierdo (formulario y filtros)
left_panel = ttk.Frame(main_frame, width=400)
left_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

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
        
ttk.Button(form_frame, text="Agregar Tarea", command=self.add_task).grid(row=6, column=1, pady=10)

# ---------------------------
# Panel izquierdo - Formulario
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
        
ttk.Button(filter_frame, text="Aplicar Filtros", command=self.apply_filters).grid(row=3, column=1, pady=10)

# ---------------------------
# Panel Derecho - Lista de Tareas
# ---------------------------
task_frame = ttk.LabelFrame(right_panel, text="Lista de Tareas", padding=10)
task_frame.pack(fill=tk.BOTH, expand=True)

#Treeview para mostrar las tareas 

