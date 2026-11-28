CREATE DATABASE IF NOT EXISTS heladeria_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE heladeria_db;

-- 1. EMPLEADO
CREATE TABLE empleado (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    apellido VARCHAR(60) NOT NULL,
    telefono VARCHAR(20),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

-- 2. PROVEEDOR
CREATE TABLE proveedor (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(150)
);

-- 3. PRODUCTO (Superentidad)
CREATE TABLE producto (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    unidad_medida ENUM('unidad', 'kg', 'litro', 'paquete', 'oz') NOT NULL,
    tipo ENUM('helado', 'vaso', 'insumo') NOT NULL,
    cantidad_actual DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (cantidad_actual >= 0),
    cantidad_minima DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (cantidad_minima >= 0),
    cantidad_optima DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (cantidad_optima >= 0),
    -- Atributo derivado (RF-06)
    estado VARCHAR(15) GENERATED ALWAYS AS (
        CASE
            WHEN cantidad_actual <= 0 THEN 'Agotado'
            WHEN cantidad_actual <= cantidad_minima THEN 'Bajo'
            ELSE 'Disponible'
        END
    ) VIRTUAL,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

-- Subentidades de PRODUCTO
CREATE TABLE helado (
    id_producto INT PRIMARY KEY,
    sabor VARCHAR(60) NOT NULL,
    presentacion_oz INT NOT NULL CHECK (presentacion_oz IN (9, 12, 16)),
    incluye_toppings BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);

CREATE TABLE vaso (
    id_producto INT PRIMARY KEY,
    capacidad_oz INT NOT NULL CHECK (capacidad_oz IN (9, 12, 16)),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);

CREATE TABLE insumo (
    id_producto INT PRIMARY KEY,
    tipo_insumo ENUM('topping', 'salsa', 'desechable') NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);

-- 4. COMPRA
CREATE TABLE compra (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    id_proveedor INT NOT NULL,
    numero_factura VARCHAR(50),
    FOREIGN KEY (id_proveedor) REFERENCES proveedor(id_proveedor)
);

-- Relación N:M COMPRA - PRODUCTO (contiene)
CREATE TABLE detalle_compra (
    id_compra INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL CHECK (precio_unitario >= 0),
    PRIMARY KEY (id_compra, id_producto),
    FOREIGN KEY (id_compra) REFERENCES compra(id_compra),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);

-- Relación N:M EMPLEADO - PRODUCTO (registra_movimiento)
CREATE TABLE movimiento (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_empleado INT NOT NULL,
    id_producto INT NOT NULL,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_movimiento ENUM('entrada', 'salida', 'cierre', 'ajuste') NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL CHECK (cantidad >= 0),
    observaciones VARCHAR(255),
    FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);

-- Relacion N:M HELADO - INSUMO
CREATE TABLE helado_insumo (
    id_helado INT NOT NULL,
    id_insumo INT NOT NULL,
    cantidad_requerida DECIMAL(10,2) NOT NULL CHECK (cantidad_requerida > 0),
    PRIMARY KEY (id_helado, id_insumo),
    FOREIGN KEY (id_helado) REFERENCES helado(id_producto),
    FOREIGN KEY (id_insumo) REFERENCES insumo(id_producto)
);

-- Indices para agilizar reportes y búsquedas (RNF-05)
CREATE INDEX idx_compra_fecha ON compra(fecha);
CREATE INDEX idx_movimiento_fecha ON movimiento(fecha_hora);