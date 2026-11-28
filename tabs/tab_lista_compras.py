from tkinter import ttk


class TabListaCompras(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app

        ttk.Button(self, text="Actualizar lista", command=self.cargar_lista_compras).pack(anchor="e", pady=5)

        cols = ("Producto", "Tipo", "Actual", "Óptima", "Estado", "Sugerido Pedir")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="center")
        self.tree.column("Producto", width=200, anchor="w")
        self.tree.pack(expand=True, fill="both")

        self.cargar_lista_compras()

    def cargar_lista_compras(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        cursor = self.app.conn.cursor()
        cursor.execute("""
            SELECT producto, tipo, cantidad_actual, cantidad_optima, estado, cantidad_sugerida
            FROM vista_lista_compras
        """)
        for fila in cursor.fetchall():
            self.tree.insert("", "end", values=fila)
        cursor.close()