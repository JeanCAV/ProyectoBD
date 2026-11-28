import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


class TabMovimientos(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app
        self.empleados = {}
        self.filas = []

        # Barra superior
        barra_sup = ttk.Frame(self)
        barra_sup.pack(fill="x", pady=(0, 8))

        ttk.Label(barra_sup, text="Empleado:").pack(side="left", padx=(0, 6))
        self.cb_emp = ttk.Combobox(barra_sup, state="readonly", width=32)
        self.cb_emp.pack(side="left", padx=(0, 12))

        ttk.Button(barra_sup, text="Actualizar lista", command=self.cargar_filas).pack(side="right")

        # Contenedor con scroll
        contenedor = ttk.Frame(self)
        contenedor.pack(expand=True, fill="both")

        self.canvas = tk.Canvas(contenedor, highlightthickness=0)
        scrollbar = ttk.Scrollbar(contenedor, orient="vertical", command=self.canvas.yview)
        self.frame_filas = ttk.Frame(self.canvas)

        self.frame_filas.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.frame_filas, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(self, text="Guardar Movimientos", command=self.guardar_movimientos).pack(pady=10)

        self.cargar_empleados_combo()
        self.cargar_filas()

    def cargar_empleados_combo(self):
        cursor = self.app.conn.cursor()
        cursor.execute("SELECT id_empleado, CONCAT(nombre, ' ', apellido) FROM empleado WHERE activo = TRUE")
        self.empleados = {f"{id_e} - {nom}": id_e for id_e, nom in cursor.fetchall()}
        cursor.close()
        self.cb_emp["values"] = list(self.empleados.keys())

    def cargar_filas(self):
        for widget in self.frame_filas.winfo_children():
            widget.destroy()
        self.filas = []

        encabezados = [
            ("Producto", 28),
            ("Stock Actual", 12),
            ("Cantidad", 12),
            ("Tipo de movimiento", 16),
            ("Observaciones", 30)
        ]
        for col, (texto, ancho) in enumerate(encabezados):
            ttk.Label(
                self.frame_filas, text=texto, font=("Arial", 9, "bold"), width=ancho, anchor="w"
            ).grid(row=0, column=col, padx=5, pady=5, sticky="w")

        cursor = self.app.conn.cursor()
        cursor.execute("""
            SELECT id_producto, nombre, cantidad_actual, unidad_medida
            FROM producto WHERE activo = TRUE ORDER BY id_producto
        """)
        productos_db = cursor.fetchall()
        cursor.close()

        for i, (id_p, nom, cant_act, unidad) in enumerate(productos_db, start=1):
            ttk.Label(self.frame_filas, text=nom, width=28, anchor="w").grid(row=i, column=0, padx=5, pady=3, sticky="w")
            ttk.Label(self.frame_filas, text=f"{cant_act} {unidad}", width=12, anchor="w").grid(row=i, column=1, padx=5, pady=3, sticky="w")

            entry_cant = ttk.Entry(self.frame_filas, width=12)
            entry_cant.grid(row=i, column=2, padx=5, pady=3)

            cb_tipo = ttk.Combobox(self.frame_filas, values=["salida", "cierre", "entrada", "ajuste"], state="readonly", width=14)
            cb_tipo.set("salida")
            cb_tipo.grid(row=i, column=3, padx=5, pady=3)

            entry_obs = ttk.Entry(self.frame_filas, width=32)
            entry_obs.grid(row=i, column=4, padx=5, pady=3)

            self.filas.append({
                "id_producto": id_p,
                "nombre": nom,
                "entry_cant": entry_cant,
                "cb_tipo": cb_tipo,
                "entry_obs": entry_obs
            })

    def guardar_movimientos(self):
        emp_sel = self.cb_emp.get()
        if emp_sel not in self.empleados:
            messagebox.showwarning("Faltan datos", "Selecciona el empleado que registra los movimientos.")
            return
        id_emp = self.empleados[emp_sel]

        movimientos_a_guardar = []
        for fila in self.filas:
            cant_txt = fila["entry_cant"].get().strip()
            if cant_txt == "":
                continue
            try:
                cant = float(cant_txt)
                if cant < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Dato inválido", f"La cantidad en '{fila['nombre']}' debe ser un número válido (0 o mayor).")
                return

            movimientos_a_guardar.append((id_emp, fila["id_producto"], fila["cb_tipo"].get(), cant, fila["entry_obs"].get().strip()))

        if not movimientos_a_guardar:
            messagebox.showwarning("Sin cambios", "Ingresa una cantidad en al menos un producto antes de guardar.")
            return

        try:
            cursor = self.app.conn.cursor()
            cursor.executemany("""
                INSERT INTO movimiento (id_empleado, id_producto, tipo_movimiento, cantidad, observaciones)
                VALUES (%s, %s, %s, %s, %s)
            """, movimientos_a_guardar)
            self.app.conn.commit()
            cursor.close()

            messagebox.showinfo("Éxito", f"Se guardaron {len(movimientos_a_guardar)} movimiento(s) correctamente.")
            self.app.refrescar_stock()
        except mysql.connector.Error as err:
            self.app.conn.rollback()
            messagebox.showerror("Error en MySQL", f"Operación bloqueada:\n{err}")