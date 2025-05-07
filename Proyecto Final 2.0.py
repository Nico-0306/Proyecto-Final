import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime

class MiniTaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Gestor")
        self.root.geometry("800x500")
        self.tasks = []
        
        # UI Básica
        self.create_ui()
    
    def create_ui(self):
        # Formulario
        form = ttk.LabelFrame(self.root, text="Tarea", padding=10)
        form.pack(fill=tk.X, padx=10, pady=5)
        
        self.title_var = tk.StringVar()
        self.date_var = tk.StringVar()
        
        ttk.Label(form, text="Título:").grid(row=0, column=0)
        ttk.Entry(form, textvariable=self.title_var).grid(row=0, column=1)
        
        ttk.Label(form, text="Fecha:").grid(row=1, column=0)
        ttk.Entry(form, textvariable=self.date_var).grid(row=1, column=1)
        ttk.Button(form, text="📅", command=self.pick_date).grid(row=1, column=2)
        
        ttk.Button(form, text="Agregar", command=self.add_task).grid(row=2, column=1, pady=5)
        
        # Lista
        self.tree = ttk.Treeview(self.root, columns=("title", "date"), show="headings")
        self.tree.heading("title", text="Título")
        self.tree.heading("date", text="Fecha")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Eliminar", command=self.del_task).pack(side=tk.LEFT)
    
    def pick_date(self):
        def set_date():
            self.date_var.set(cal.get_date())
            top.destroy()
        
        top = tk.Toplevel(self.root)
        Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd').pack(padx=10, pady=10)
        ttk.Button(top, text="OK", command=set_date).pack(pady=5)
    
    def add_task(self):
        if not self.title_var.get():
            messagebox.showerror("Error", "Título requerido")
            return
            
        self.tasks.append({
            "title": self.title_var.get(),
            "date": self.date_var.get() or "Sin fecha"
        })
        
        self.update_list()
        self.title_var.set("")
        self.date_var.set("")
    
    def del_task(self):
        if not self.tree.selection():
            return
            
        if messagebox.askyesno("Confirmar", "¿Eliminar tarea?"):
            self.tree.delete(self.tree.selection()[0])
    
    def update_list(self):
        self.tree.delete(*self.tree.get_children())
        for task in self.tasks:
            self.tree.insert("", tk.END, values=(task["title"], task["date"]))

if __name__ == "__main__":
    root = tk.Tk()
    app = MiniTaskManager(root)
    root.mainloop()
    