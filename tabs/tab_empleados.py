import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


class TabEmpleados(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=15)
        self.app = app

        form = ttk.LabelFrame(self, text="Nuevo Empleado", padding=10)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_nom = ttk.Entry(form, width=20)
        self.entry_nom.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Apellido:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_ape = ttk.Entry(form, width=20)
        self.entry_ape.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Teléfono:").grid(row=0, column=4, padx=5, pady=5)
        self.entry_tel = ttk.Entry(form, width=15)
        self.entry_tel.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(form, text="Agregar", command=self.agregar_empleado).grid(row=0, column=6, padx=10)

        cols = ("ID", "Nombre", "Apellido", "Teléfono", "Estado")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=140, anchor="center")
        self.tree.pack(expand=True, fill="both")

        ttk.Button(
            self,
            text="Activar / Desactivar empleado seleccionado",
            command=self.cambiar_estado_empleado
        ).pack(pady=8)

        self.cargar_empleados()

    def cargar_empleados(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        cursor = self.app.conn.cursor()
        cursor.execute("SELECT id_empleado, nombre, apellido, telefono, activo FROM empleado ORDER BY id_empleado")
        for id_e, nom, ape, tel, act in cursor.fetchall():
            estado = "Activo" if act else "Inactivo"
            self.tree.insert("", "end", values=(id_e, nom, ape, tel, estado))
        cursor.close()

    def agregar_empleado(self):
        nom = self.entry_nom.get().strip()
        ape = self.entry_ape.get().strip()
        tel = self.entry_tel.get().strip()
        if not nom or not ape:
            messagebox.showwarning("Faltan datos", "Nombre y apellido son obligatorios.")
            return
        try:
            cursor = self.app.conn.cursor()
            cursor.execute(
                "INSERT INTO empleado (nombre, apellido, telefono) VALUES (%s, %s, %s)",
                (nom, ape, tel)
            )
            self.app.conn.commit()
            cursor.close()

            self.entry_nom.delete(0, tk.END)
            self.entry_ape.delete(0, tk.END)
            self.entry_tel.delete(0, tk.END)
            self.cargar_empleados()
            self.app.refrescar_empleados()
            messagebox.showinfo("Éxito", "Empleado agregado correctamente.")
        except mysql.connector.Error as err:
            self.app.conn.rollback()
            messagebox.showerror("Error en MySQL", str(err))

    def cambiar_estado_empleado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Haz clic sobre un empleado en la tabla primero.")
            return
        valores = self.tree.item(seleccion[0], "values")
        id_emp = valores[0]
        nuevo_estado = False if valores[4] == "Activo" else True

        try:
            cursor = self.app.conn.cursor()
            cursor.execute("UPDATE empleado SET activo = %s WHERE id_empleado = %s", (nuevo_estado, id_emp))
            self.app.conn.commit()
            cursor.close()

            self.cargar_empleados()
            self.app.refrescar_empleados()
        except mysql.connector.Error as err:
            self.app.conn.rollback()
            messagebox.showerror("Error en MySQL", str(err))