from tkinter import ttk


class TabInventario(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app

        ttk.Button(self, text="Actualizar tabla", command=self.cargar_inventario).pack(anchor="e", pady=5)

        cols = ("ID", "Producto", "Tipo", "Actual", "Mínima", "Óptima", "Estado")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=110, anchor="center")
        self.tree.column("Producto", width=200, anchor="w")
        self.tree.pack(expand=True, fill="both")

        self.cargar_inventario()

    def cargar_inventario(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        cursor = self.app.conn.cursor()
        cursor.execute("""
            SELECT id_producto, nombre, tipo, cantidad_actual, cantidad_minima, cantidad_optima, estado
            FROM producto WHERE activo = TRUE ORDER BY id_producto
        """)
        for fila in cursor.fetchall():
            self.tree.insert("", "end", values=fila)
        cursor.close()