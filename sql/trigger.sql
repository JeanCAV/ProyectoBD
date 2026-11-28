USE heladeria_db;

DELIMITER //

-- 1. Al registrar una compra, suma automáticamente al stock del producto
CREATE TRIGGER trg_compra_suma_stock
AFTER INSERT ON detalle_compra
FOR EACH ROW
BEGIN
    UPDATE producto
    SET cantidad_actual = cantidad_actual + NEW.cantidad
    WHERE id_producto = NEW.id_producto;
END //

-- 2. Al registrar un movimiento, actualiza stock y descuenta insumos de la receta (RF-05)
CREATE TRIGGER trg_movimiento_actualiza_stock
AFTER INSERT ON movimiento
FOR EACH ROW
BEGIN
    IF NEW.tipo_movimiento = 'entrada' THEN
        UPDATE producto
        SET cantidad_actual = cantidad_actual + NEW.cantidad
        WHERE id_producto = NEW.id_producto;

    ELSEIF NEW.tipo_movimiento = 'salida' THEN
        -- Descuenta el producto principal
        UPDATE producto
        SET cantidad_actual = cantidad_actual - NEW.cantidad
        WHERE id_producto = NEW.id_producto;

        -- Si es un helado con insumos asociados, descuenta los insumos automáticamente
        UPDATE producto p
        JOIN helado_insumo hi ON p.id_producto = hi.id_insumo
        SET p.cantidad_actual = p.cantidad_actual - (hi.cantidad_requerida * NEW.cantidad)
        WHERE hi.id_helado = NEW.id_producto;
    END IF;
END //

DELIMITER ;