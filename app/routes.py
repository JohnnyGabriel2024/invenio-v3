# VERSIÓN FINAL CORREGIDA
from flask import request, redirect, render_template_string
from datetime import datetime
from app.db import query
from app.logica import confirmar_pedido


def register_routes(app):

    @app.route("/")
    def index():
        categorias = query("SELECT * FROM categories")

        productos = query("""
            SELECT p.id, p.name, p.stock, c.name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
        """)

        clientes = query("SELECT * FROM clients")
        proveedores = query("SELECT * FROM suppliers")

        pedidos = query("""
            SELECT o.id, c.name, o.created_at
            FROM orders o
            JOIN clients c ON o.client_id = c.id
            ORDER BY o.id DESC
        """)

        movimientos = query("""
            SELECT 
                m.id,
                p.name,
                c.name,
                m.type,
                m.quantity,
                m.created_at,
                s.name
            FROM movements m
            JOIN products p ON m.product_id = p.id
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON m.supplier_id = s.id
            ORDER BY m.id DESC
            LIMIT 15
        """)

        return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Inventario</title>

<style>
:root {
  --bg:#f4f6f8;
  --card:#ffffff;
  --primary:#1976d2;
  --success:#2e7d32;
  --danger:#c62828;
  --muted:#777;
}

body {
  margin:0;
  font-family: Arial, sans-serif;
  background:var(--bg);
}

.container {
  max-width:1200px;
  margin:auto;
  padding:1.5rem;
}

.section {
  background:var(--card);
  padding:1.25rem;
  margin-bottom:1.5rem;
  border-radius:8px;
  box-shadow:0 2px 6px rgba(0,0,0,.06);
}

h1 { margin-bottom:1.5rem; }
h3 { margin-top:0; }

.grid-2 {
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:1rem;
}

input, select {
  padding:.45rem;
  margin-right:.4rem;
}

button {
  padding:.45rem .8rem;
  border:none;
  border-radius:4px;
  background:var(--primary);
  color:white;
  cursor:pointer;
}

button.success { background:var(--success); }

ul { list-style:none; padding:0; margin:0; }
li { padding:.4rem 0; border-bottom:1px solid #eee; }

.muted { color:var(--muted); }
.in { color:var(--success); }
.out { color:var(--danger); }
</style>
</head>

<body>
<div class="container">

<h1>📦 Sistema de Inventario</h1>

<!-- ================= Entrada de stock ================= -->

<div class="section">
<h3>➕ Entrada de stock</h3>
<form method="post" action="/inventory/entry">
<select name="product_id">
{% for p in productos %}
<option value="{{ p[0] }}">{{ p[1] }}</option>
{% endfor %}
</select>

<select name="supplier_id">
<option value="">— Proveedor (opcional) —</option>
{% for s in proveedores %}
<option value="{{ s[0] }}">{{ s[1] }}</option>
{% endfor %}
</select>

<input type="number" name="quantity" required>
<button class="success">Agregar</button>
</form>
</div>

<!-- ================= Proveedores y Clientes ================= -->

<div class="grid-2">

<div class="section">
<h3>Proveedores</h3>
<form method="post" action="/suppliers/create">
<input name="name" placeholder="Proveedor" required>
<button>Crear</button>
</form>
<ul>
{% for s in proveedores %}
<li>{{ s[1] }}</li>
{% endfor %}
</ul>
</div>

<div class="section">
<h3>Clientes</h3>
<form method="post" action="/clients/create">
<input name="name" placeholder="Cliente" required>
<button>Crear</button>
</form>
<ul>
{% for c in clientes %}
<li>{{ c[1] }}</li>
{% endfor %}
</ul>
</div>

</div>

<!-- ================= Productos ================= -->

<div class="section">
<h3>Productos</h3>

<form method="post" action="/products/create">
<input name="name" placeholder="Nombre del producto" required>

<select name="category_id">
<option value="">Sin categoría</option>
{% for c in categorias %}
<option value="{{ c[0] }}">{{ c[1] }}</option>
{% endfor %}
</select>

<button>Crear producto</button>
</form>

<ul>
{% for p in productos %}
<li>
<strong>{{ p[1] }}</strong>
<span class="muted">({{ p[3] }})</span>
— Stock: {{ p[2] }}
</li>
{% endfor %}
</ul>
</div>

<!-- ================= Pedidos ================= -->

<div class="section">
<h3>Pedidos</h3>

<form method="post" action="/orders/create">
<select name="client_id">
{% for c in clientes %}
<option value="{{ c[0] }}">{{ c[1] }}</option>
{% endfor %}
</select>
<button>Crear pedido</button>
</form>

<ul>
{% for p in pedidos %}
<li>
<strong>Pedido #{{ p[0] }}</strong> — {{ p[1] }}

<form method="post" action="/orders/{{ p[0] }}/items/create">
<select name="product_id">
{% for prod in productos %}
<option value="{{ prod[0] }}">{{ prod[1] }}</option>
{% endfor %}
</select>
<input type="number" name="quantity" required>
<button>Agregar ítem</button>
</form>

<form method="post" action="/orders/{{ p[0] }}/confirm">
<button>Confirmar</button>
</form>
</li>
{% endfor %}
</ul>
</div>

<!-- ================= Movimientos ================= -->

<div class="section">
<h3>📊 Últimos movimientos</h3>
<ul>
{% for m in movimientos %}
<li>
<strong>{{ m[1] }}</strong>
<span class="muted">({{ m[2] }})</span>
—
<span class="{{ 'in' if m[3]=='entrada' else 'out' }}">{{ m[3] }}</span>
|
Cantidad: {{ m[4] }}
{% if m[6] %}
| Proveedor: {{ m[6] }}
{% endif %}
|
<span class="muted">{{ m[5] }}</span>
</li>
{% endfor %}
</ul>
</div>

</div>
</body>
</html>
""",
        categorias=categorias,
        productos=productos,
        clientes=clientes,
        proveedores=proveedores,
        pedidos=pedidos,
        movimientos=movimientos
        )

    # ================= Proveedores =================

    @app.route("/suppliers/create", methods=["POST"])
    def crear_proveedor():
        query("INSERT INTO suppliers (name) VALUES (?)", (request.form["name"],))
        return redirect("/")

    # ================= Clientes =================

    @app.route("/clients/create", methods=["POST"])
    def crear_cliente():
        query("INSERT INTO clients (name) VALUES (?)", (request.form["name"],))
        return redirect("/")

    # ================= Productos =================

    @app.route("/products/create", methods=["POST"])
    def crear_producto():
        name = request.form.get("name")
        category_id = request.form.get("category_id") or None

        if name:
            query(
                "INSERT INTO products (name, category_id, stock) VALUES (?, ?, 0)",
                (name, category_id)
            )

        return redirect("/")

    # ================= Inventario =================

    @app.route("/inventory/entry", methods=["POST"])
    def entrada_stock():
        product_id = request.form["product_id"]
        supplier_id = request.form.get("supplier_id") or None
        quantity = int(request.form["quantity"])

        query(
            """
            INSERT INTO movements
            (product_id, supplier_id, type, quantity, created_at)
            VALUES (?, ?, 'entrada', ?, ?)
            """,
            (product_id, supplier_id, quantity, datetime.now().isoformat())
        )

        query(
            "UPDATE products SET stock = stock + ? WHERE id = ?",
            (quantity, product_id)
        )

        return redirect("/")

    # ================= Pedidos =================

    @app.route("/orders/create", methods=["POST"])
    def crear_pedido():
        query(
            "INSERT INTO orders (client_id, created_at) VALUES (?, datetime('now'))",
            (request.form["client_id"],)
        )
        return redirect("/")

    @app.route("/orders/<int:order_id>/items/create", methods=["POST"])
    def agregar_item(order_id):
        query(
            "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
            (order_id, request.form["product_id"], request.form["quantity"])
        )
        return redirect("/")

    @app.route("/orders/<int:order_id>/confirm", methods=["POST"])
    def confirmar(order_id):
        confirmar_pedido(order_id)
        return redirect("/")
