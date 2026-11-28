import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import mysql.connector


class TabRegistrarCompra(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=20)
        self.app = app
        self.proveedores = {}
        self.productos = {}

        ttk.Label(self, text="Fecha (AAAA-MM-DD):").grid(row=0, column=0, sticky="e", pady=6, padx=5)
        self.entry_fecha = ttk.Entry(self, width=38)
        self.entry_fecha.insert(0, str(date.today()))
        self.entry_fecha.grid(row=0, column=1, pady=6)

        ttk.Label(self, text="Proveedor:").grid(row=1, column=0, sticky="e", pady=6, padx=5)
        self.cb_prov = ttk.Combobox(self, state="readonly", width=35)
        self.cb_prov.grid(row=1, column=1, pady=6)

        ttk.Label(self, text="N° Factura:").grid(row=2, column=0, sticky="e", pady=6, padx=5)
        self.entry_fact = ttk.Entry(self, width=38)
        self.entry_fact.grid(row=2, column=1, pady=6)

        ttk.Label(self, text="Producto comprado:").grid(row=3, column=0, sticky="e", pady=6, padx=5)
        self.cb_prod = ttk.Combobox(self, state="readonly", width=35)
        self.cb_prod.grid(row=3, column=1, pady=6)

        ttk.Label(self, text="Cantidad:").grid(row=4, column=0, sticky="e", pady=6, padx=5)
        self.entry_cant = ttk.Entry(self, width=38)
        self.entry_cant.grid(row=4, column=1, pady=6)

        ttk.Label(self, text="Precio Unitario:").grid(row=5, column=0, sticky="e", pady=6, padx=5)
        self.entry_precio = ttk.Entry(self, width=38)
        self.entry_precio.grid(row=5, column=1, pady=6)

        ttk.Button(self, text="Guardar Compra", command=self.guardar_compra).grid(row=6, column=0, columnspan=2, pady=15)

        self.cargar_combos()

    def cargar_combos(self):
        cursor = self.app.conn.cursor()
        cursor.execute("SELECT id_proveedor, nombre FROM proveedor ORDER BY id_proveedor")
        self.proveedores = {f"{id_p} - {nom}": id_p for id_p, nom in cursor.fetchall()}

        cursor.execute("SELECT id_producto, nombre FROM producto WHERE activo = TRUE ORDER BY id_producto")
        self.productos = {f"{id_p} - {nom}": id_p for id_p, nom in cursor.fetchall()}
        cursor.close()

        self.cb_prov["values"] = list(self.proveedores.keys())
        self.cb_prod["values"] = list(self.productos.keys())

    def guardar_compra(self):
        try:
            fecha = self.entry_fecha.get().strip()
            id_prov = self.proveedores[self.cb_prov.get()]
            factura = self.entry_fact.get().strip()
            id_prod = self.productos[self.cb_prod.get()]
            cant = float(self.entry_cant.get())
            precio = float(self.entry_precio.get())

            cursor = self.app.conn.cursor()
            cursor.execute(
                "INSERT INTO compra (fecha, id_proveedor, numero_factura) VALUES (%s, %s, %s)",
                (fecha, id_prov, factura)
            )
            id_compra = cursor.lastrowid
            cursor.execute(
                "INSERT INTO detalle_compra (id_compra, id_producto, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
                (id_compra, id_prod, cant, precio)
            )
            self.app.conn.commit()
            cursor.close()

            messagebox.showinfo("Éxito", f"Compra #{id_compra} guardada y stock actualizado.")
            self.entry_fact.delete(0, tk.END)
            self.entry_cant.delete(0, tk.END)
            self.entry_precio.delete(0, tk.END)
            self.app.refrescar_stock()
        except KeyError:
            messagebox.showwarning("Faltan datos", "Selecciona un proveedor y un producto.")
        except ValueError:
            messagebox.showwarning("Dato inválido", "Cantidad y precio deben ser números.")
        except mysql.connector.Error as err:
            self.app.conn.rollback()
            messagebox.showerror("Error en MySQL", str(err))