-- Usuario Administrador (acceso total)
CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'Admin2026!';
GRANT ALL PRIVILEGES ON heladeria_db.* TO 'admin_heladeria'@'localhost';

-- Usuario Empleado (solo consulta productos/empleados/lista de compras y registra movimientos)
CREATE USER IF NOT EXISTS 'empleado'@'localhost' IDENTIFIED BY 'Empleado2026!';
GRANT SELECT ON heladeria_db.producto TO 'empleado_heladeria'@'localhost';
GRANT SELECT ON heladeria_db.empleado TO 'empleado_heladeria'@'localhost';
GRANT SELECT ON heladeria_db.vista_lista_compras TO 'empleado_heladeria'@'localhost';
GRANT SELECT, INSERT ON heladeria_db.movimiento TO 'empleado_heladeria'@'localhost';

FLUSH PRIVILEGES;