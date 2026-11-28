import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

from tabs.tab_inventario import TabInventario
from tabs.tab_movimientos import TabMovimientos
from tabs.tab_lista_compras import TabListaCompras
from tabs.tab_registrar_compra import TabRegistrarCompra
from tabs.tab_reporte_diario import TabReporteDiario
from tabs.tab_empleados import TabEmpleados
from tabs.tab_productos_proveedores import TabProductosProveedores


class AppHeladeria:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Inventario - Heladería")
        self.root.geometry("880x540")
        self.conn = None
        self.usuario_actual = ""

        # Referencias a pestañas (para refrescarlas entre sí)
        self.tab_inventario = None
        self.tab_movimientos = None
        self.tab_lista_compras = None
        self.tab_registrar_compra = None
        self.tab_reporte = None
        self.tab_empleados = None
        self.tab_productos_prov = None

        self.mostrar_login()

    # ---------------- LOGIN ----------------
    def mostrar_login(self):
        self.limpiar_ventana()
        frame = ttk.Frame(self.root, padding=30)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(frame, text="Inicio de Sesión (MySQL)", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        ttk.Label(frame, text="Usuario:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_user = ttk.Entry(frame, width=25)
        self.entry_user.insert(0, "admin_heladeria")
        self.entry_user.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Contraseña:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_pass = ttk.Entry(frame, width=25, show="*")
        self.entry_pass.grid(row=2, column=1, pady=5)

        ttk.Button(frame, text="Ingresar", command=self.conectar).grid(row=3, column=0, columnspan=2, pady=15)

    def conectar(self):
        user = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user=user,
                password=password,
                database="heladeria_db"
            )
            self.usuario_actual = user
            self.construir_interfaz_principal()
        except mysql.connector.Error as err:
            messagebox.showerror("Error de conexión", f"No se pudo conectar:\n{err}")

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def cerrar_sesion(self):
        if self.conn:
            self.conn.close()
            self.conn = None
        self.mostrar_login()

    # ---------------- INTERFAZ PRINCIPAL ----------------
    def construir_interfaz_principal(self):
        self.limpiar_ventana()

        barra = ttk.Frame(self.root, padding=8)
        barra.pack(fill="x")
        ttk.Label(barra, text=f"Sesión iniciada como: {self.usuario_actual}", font=("Arial", 10, "bold")).pack(side="left")
        ttk.Button(barra, text="Cerrar sesión", command=self.cerrar_sesion).pack(side="right")

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(expand=True, fill="both", padx=10, pady=5)

        # Pestañas para TODOS (Admin y Empleado)
        self.tab_inventario = TabInventario(self.tabs, self)
        self.tabs.add(self.tab_inventario, text="Inventario Actual")

        self.tab_movimientos = TabMovimientos(self.tabs, self)
        self.tabs.add(self.tab_movimientos, text="Registrar Movimiento / Cierre")

        self.tab_lista_compras = TabListaCompras(self.tabs, self)
        self.tabs.add(self.tab_lista_compras, text="Lista de Compras")

        # Pestañas exclusivas para Administrador / root
        self.tab_registrar_compra = None
        self.tab_reporte = None
        self.tab_empleados = None
        self.tab_productos_prov = None

        if self.usuario_actual != "empleado_heladeria":
            self.tab_registrar_compra = TabRegistrarCompra(self.tabs, self)
            self.tabs.add(self.tab_registrar_compra, text="Registrar Compra")

            self.tab_reporte = TabReporteDiario(self.tabs, self)
            self.tabs.add(self.tab_reporte, text="Reporte Diario")

            self.tab_empleados = TabEmpleados(self.tabs, self)
            self.tabs.add(self.tab_empleados, text="Empleados")

            self.tab_productos_prov = TabProductosProveedores(self.tabs, self)
            self.tabs.add(self.tab_productos_prov, text="Productos y Proveedores")

    # ---------------- MÉTODOS DE SINCRONIZACIÓN ----------------
    def refrescar_stock(self):
        self.tab_inventario.cargar_inventario()
        self.tab_lista_compras.cargar_lista_compras()
        self.tab_movimientos.cargar_filas()
        if self.tab_reporte:
            self.tab_reporte.cargar_reporte()

    def refrescar_empleados(self):
        self.tab_movimientos.cargar_empleados_combo()

    def refrescar_catalogo(self):
        self.refrescar_stock()
        if self.tab_registrar_compra:
            self.tab_registrar_compra.cargar_combos()
        if self.tab_productos_prov:
            self.tab_productos_prov.cargar_combo_proveedores()
            self.tab_productos_prov.cargar_productos_proveedores()