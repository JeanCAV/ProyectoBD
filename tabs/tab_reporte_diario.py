from tkinter import ttk


class TabReporteDiario(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app

        ttk.Button(self, text="Actualizar reporte", command=self.cargar_reporte).pack(anchor="e", pady=5)

        cols = ("Fecha", "Producto", "Entradas", "Salidas", "Cierre Físico", "Stock Sistema", "Estado")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=105, anchor="center")
        self.tree.column("Producto", width=180, anchor="w")
        self.tree.pack(expand=True, fill="both")

        self.cargar_reporte()

    def cargar_reporte(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        cursor = self.app.conn.cursor()
        cursor.execute("""
            SELECT fecha, producto, total_entradas, total_salidas, conteo_fisico_cierre, stock_sistema_actual, estado
            FROM vista_reporte_diario ORDER BY fecha DESC
        """)
        for fila in cursor.fetchall():
            self.tree.insert("", "end", values=fila)
        cursor.close()