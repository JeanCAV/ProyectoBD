import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


class TabProductosProveedores(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self.proveedores = {}

        # Formulario rápido para agregar producto
        form = ttk.LabelFrame(self, text="Agregar Producto", padding=8)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, padx=4, pady=4, sticky="e")
        self.entry_nom = ttk.Entry(form, width=22)
        self.entry_nom.grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(form, text="Tipo:").grid(row=0, column=2, padx=4, pady=4, sticky="e")
        self.cb_tipo = ttk.Combobox(form, values=["insumo", "helado", "vaso"], state="readonly", width=12)
        self.cb_tipo.set("insumo")
        self.cb_tipo.grid(row=0, column=3, padx=4, pady=4)

        ttk.Label(form, text="Unidad:").grid(row=0, column=4, padx=4, pady=4, sticky="e")
        self.cb_uni = ttk.Combobox(form, values=["unidad", "kg", "litro", "paquete", "oz"], state="readonly", width=10)
        self.cb_uni.set("unidad")
        self.cb_uni.grid(row=0, column=5, padx=4, pady=4)

        ttk.Label(form, text="Proveedor:").grid(row=1, column=0, padx=4, pady=4, sticky="e")
        self.cb_prov = ttk.Combobox(form, state="readonly", width=22)
        self.cb_prov.grid(row=1, column=1, padx=4, pady=4)

        ttk.Label(form, text="Actual / Mín / Ópt:").grid(row=1, column=2, padx=4, pady=4, sticky="e")
        frame_cants = ttk.Frame(form)
        frame_cants.grid(row=1, column=3, columnspan=2, sticky="w")
        self.entry_act = ttk.Entry(frame_cants, width=6)
        self.entry_act.insert(0, "0")
        self.entry_act.pack(side="left", padx=2)
        self.entry_min = ttk.Entry(frame_cants, width=6)
        self.entry_min.insert(0, "5")
        self.entry_min.pack(side="left", padx=2)
        self.entry_opt = ttk.Entry(frame_cants, width=6)
        self.entry_opt.insert(0, "20")
        self.entry_opt.pack(side="left", padx=2)

        ttk.Button(form, text="Agregar Producto", command=self.agregar_producto).grid(row=1, column=5, padx=6, pady=4)

        # Tabla
        cols = ("ID", "Producto", "Tipo", "ID Prov", "Proveedor", "Teléfono Proveedor")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=110, anchor="center")
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("ID Prov", width=65, anchor="center")
        self.tree.column("Producto", width=210, anchor="w")
        self.tree.column("Proveedor", width=200, anchor="w")
        self.tree.pack(expand=True, fill="both")

        # Botones de acción
        acciones = ttk.Frame(self, padding=(0, 8, 0, 0))
        acciones.pack(fill="x")

        ttk.Button(acciones, text="Eliminar producto seleccionado", command=self.eliminar_producto).pack(side="left", padx=4)
        ttk.Button(acciones, text="Cambiar proveedor del producto", command=self.ventana_cambiar_proveedor).pack(side="left", padx=4)
        ttk.Button(acciones, text="Editar datos del proveedor", command=self.ventana_editar_proveedor).pack(side="right", padx=4)
        ttk.Button(acciones, text="+ Nuevo proveedor", command=self.ventana_nuevo_proveedor).pack(side="right", padx=4)

        self.cargar_combo_proveedores()
        self.cargar_productos_proveedores()

    def cargar_combo_proveedores(self):
        cursor = self.app.conn.cursor()
        cursor.execute("SELECT id_proveedor, nombre FROM proveedor ORDER BY id_proveedor")
        self.proveedores = {f"{id_p} - {nom}": id_p for id_p, nom in cursor.fetchall()}
        cursor.close()

        self.cb_prov["values"] = ["Sin proveedor"] + list(self.proveedores.keys())
        if not self.cb_prov.get():
            self.cb_prov.set("Sin proveedor")

    def cargar_productos_proveedores(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        cursor = self.app.conn.cursor()
        cursor.execute("""
            SELECT p.id_producto, p.nombre, p.tipo,
                   COALESCE(pr.id_proveedor, '-'),
                   COALESCE(pr.nombre, 'Sin proveedor'),
                   COALESCE(pr.telefono, '-')
            FROM producto p
            LEFT JOIN proveedor pr ON p.id_proveedor = pr.id_proveedor
            WHERE p.activo = TRUE
            ORDER BY p.id_producto
        """)
        for fila in cursor.fetchall():
            self.tree.insert("", "end", values=fila)
        cursor.close()

    def agregar_producto(self):
        nombre = self.entry_nom.get().strip()
        tipo = self.cb_tipo.get()
        unidad = self.cb_uni.get()
        prov_txt = self.cb_prov.get()
        id_prov = None if prov_txt in ("", "Sin proveedor") else self.proveedores.get(prov_txt)

        if not nombre:
            messagebox.showwarning("Faltan datos", "Escribe el nombre del producto.")
            return
        try:
            act = float(self.entry_act.get())
            min_c = float(self.entry_min.get())
            opt_c = float(self.entry_opt.get())

            cursor = self.app.conn.cursor()
            cursor.execute("""
                INSERT INTO producto (nombre, unidad_medida, tipo, cantidad_actual, cantidad_minima, cantidad_optima, id_proveedor)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nombre, unidad, tipo, act, min_c, opt_c, id_prov))
            id_nuevo = cursor.lastrowid

            if tipo == "helado":
                cursor.execute("INSERT INTO helado (id_producto, sabor, presentacion_oz, incluye_toppings) VALUES (%s, %s, 12, FALSE)", (id_nuevo, nombre))
            elif tipo == "vaso":
                cursor.execute("INSERT INTO vaso (id_producto, capacidad_oz) VALUES (%s, 12)", (id_nuevo,))
            else:
                cursor.execute("INSERT INTO insumo (id_producto, tipo_insumo) VALUES (%s, 'acompañamiento')", (id_nuevo,))

            self.app.conn.commit()
            cursor.close()

            self.entry_nom.delete(0, tk.END)
            self.app.refrescar_catalogo()
            messagebox.showinfo("Éxito", "Producto agregado correctamente.")
        except ValueError:
            messagebox.showwarning("Dato inválido", "Las cantidades deben ser números.")
        except mysql.connector.Error as err:
            self.app.conn.rollback()
            messagebox.showerror("Error en MySQL", str(err))

    def eliminar_producto(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Selecciona un producto de la tabla.")
            return
        id_prod, nom_prod = self.tree.item(sel[0], "values")[0:2]
        if not messagebox.askyesno("Confirmar", f"¿Eliminar '{nom_prod}' del inventario activo?"):
            return
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("UPDATE producto SET activo = FALSE WHERE id_producto = %s", (id_prod,))
            self.app.conn.commit()
            cursor.close()
            self.app.refrescar_catalogo()
        except mysql.connector.Error as err:
            self.app.conn.rollback()
            messagebox.showerror("Error en MySQL", str(err))

    def ventana_cambiar_proveedor(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Selecciona un producto de la tabla.")
            return
        id_prod, nom_prod = self.tree.item(sel[0], "values")[0:2]

        win = tk.Toplevel(self.app.root)
        win.title("Cambiar Proveedor")
        win.geometry("340x140")
        ttk.Label(win, text=f"Producto: {nom_prod}").pack(pady=8)
        cb = ttk.Combobox(win, values=["Sin proveedor"] + list(self.proveedores.keys()), state="readonly", width=32)
        cb.set("Sin proveedor")
        cb.pack(pady=5)

        def guardar():
            val = cb.get()
            id_prov = None if val == "Sin proveedor" else self.proveedores[val]
            try:
                cursor = self.app.conn.cursor()
                cursor.execute("UPDATE producto SET id_proveedor = %s WHERE id_producto = %s", (id_prov, id_prod))
                self.app.conn.commit()
                cursor.close()
                self.cargar_productos_proveedores()
                win.destroy()
            except mysql.connector.Error as err:
                self.app.conn.rollback()
                messagebox.showerror("Error en MySQL", str(err))

        ttk.Button(win, text="Guardar", command=guardar).pack(pady=10)

    def ventana_nuevo_proveedor(self):
        win = tk.Toplevel(self.app.root)
        win.title("Nuevo Proveedor")
        win.geometry("340x190")

        ttk.Label(win, text="Nombre:").grid(row=0, column=0, padx=8, pady=6, sticky="e")
        e_nom = ttk.Entry(win, width=26)
        e_nom.grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(win, text="Teléfono:").grid(row=1, column=0, padx=8, pady=6, sticky="e")
        e_tel = ttk.Entry(win, width=26)
        e_tel.grid(row=1, column=1, padx=8, pady=6)

        ttk.Label(win, text="Dirección:").grid(row=2, column=0, padx=8, pady=6, sticky="e")
        e_dir = ttk.Entry(win, width=26)
        e_dir.grid(row=2, column=1, padx=8, pady=6)

        def guardar():
            nom = e_nom.get().strip()
            if not nom:
                messagebox.showwarning("Faltan datos", "El nombre del proveedor es obligatorio.", parent=win)
                return
            try:
                cursor = self.app.conn.cursor()
                cursor.execute(
                    "INSERT INTO proveedor (nombre, telefono, direccion) VALUES (%s, %s, %s)",
                    (nom, e_tel.get().strip(), e_dir.get().strip())
                )
                self.app.conn.commit()
                cursor.close()
                self.app.refrescar_catalogo()
                win.destroy()
            except mysql.connector.Error as err:
                self.app.conn.rollback()
                messagebox.showerror("Error en MySQL", str(err), parent=win)

        ttk.Button(win, text="Guardar Proveedor", command=guardar).grid(row=3, column=0, columnspan=2, pady=12)

    def ventana_editar_proveedor(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Selecciona un producto que tenga proveedor asignado.")
            return
        id_prov = self.tree.item(sel[0], "values")[3]
        if id_prov == "-":
            messagebox.showwarning("Sin proveedor", "Este producto aún no tiene proveedor. Usa 'Cambiar proveedor' primero.")
            return

        cursor = self.app.conn.cursor()
        cursor.execute("SELECT nombre, telefono, direccion FROM proveedor WHERE id_proveedor = %s", (id_prov,))
        nom_act, tel_act, dir_act = cursor.fetchone()
        cursor.close()

        win = tk.Toplevel(self.app.root)
        win.title(f"Editar Proveedor #{id_prov}")
        win.geometry("340x190")

        ttk.Label(win, text="Nombre:").grid(row=0, column=0, padx=8, pady=6, sticky="e")
        e_nom = ttk.Entry(win, width=26)
        e_nom.insert(0, nom_act or "")
        e_nom.grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(win, text="Teléfono:").grid(row=1, column=0, padx=8, pady=6, sticky="e")
        e_tel = ttk.Entry(win, width=26)
        e_tel.insert(0, tel_act or "")
        e_tel.grid(row=1, column=1, padx=8, pady=6)

        ttk.Label(win, text="Dirección:").grid(row=2, column=0, padx=8, pady=6, sticky="e")
        e_dir = ttk.Entry(win, width=26)
        e_dir.insert(0, dir_act or "")
        e_dir.grid(row=2, column=1, padx=8, pady=6)

        def guardar():
            nom = e_nom.get().strip()
            if not nom:
                messagebox.showwarning("Faltan datos", "El nombre es obligatorio.", parent=win)
                return
            try:
                cursor = self.app.conn.cursor()
                cursor.execute(
                    "UPDATE proveedor SET nombre = %s, telefono = %s, direccion = %s WHERE id_proveedor = %s",
                    (nom, e_tel.get().strip(), e_dir.get().strip(), id_prov)
                )
                self.app.conn.commit()
                cursor.close()
                self.app.refrescar_catalogo()
                win.destroy()
            except mysql.connector.Error as err:
                self.app.conn.rollback()
                messagebox.showerror("Error en MySQL", str(err), parent=win)

        ttk.Button(win, text="Actualizar Proveedor", command=guardar).grid(row=3, column=0, columnspan=2, pady=12)