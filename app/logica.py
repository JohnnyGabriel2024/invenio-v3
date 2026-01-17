from datetime import datetime
from app.db import query


def calcular_delta(tipo, cantidad):
    if tipo == "salida":
        return -cantidad
    return cantidad


def confirmar_pedido(order_id):
    items = query(
        "SELECT product_id, quantity FROM order_items WHERE order_id = ?",
        (order_id,)
    )

    for product_id, quantity in items:
        # movimiento de salida por pedido
        query(
            """
            INSERT INTO movements (product_id, type, quantity, created_at)
            VALUES (?, 'salida', ?, ?)
            """,
            (product_id, -quantity, datetime.now().isoformat())
        )

        # actualizar stock
        query(
            "UPDATE products SET stock = stock + ? WHERE id = ?",
            (-quantity, product_id)
        )

