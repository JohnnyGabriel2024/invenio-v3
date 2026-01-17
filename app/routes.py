# UI RESPONSIVA Y PROFESIONAL
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
            LIMIT 20
        """)

        return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Inventario</title>

<style>
:root {
  --bg:#f3f5f8;
  --card:#ffffff;
  --primary:#1f4fd8;
  --success:#2e7d32;
  --danger:#c62828;
  --text:#2c2c2c;
  --muted:#6f6f6f;
  --border:#e0e0e0;
}

* { box-sizing:border-box; }

body {
  margin:0;
  font-family: "Segoe UI", Arial, sans-serif;
  background:var(--bg);
  color:var(--text);
}

header {
  background:var(--primary);
  color:white;
  padding:1rem;
}

header h1 {
  margin:0;
  font-size:1.4rem;
}

.container {
  max-width:1200px;
  margin:auto;
  padding:1rem;
}

.section {
  background:var(--card);
  border-radius:10px;
  padding:1rem;
  margin-bottom:1rem;
  box-shadow:0 4px 10px rgba(0,0,0,.05);
}

.section h3 {
  margin-top:0;
  font-size:1.1rem;
}

.grid {
  display:grid;
  grid-template-columns:1fr;
  gap:1rem;
}

@media (min-width: 768px) {
  .grid-2 { grid-template-columns:1fr 1fr; }
}

@media (min-width: 1024px) {
  .grid-3 { grid-template-columns:1fr 1fr 1fr; }
}

form {
  display:flex;
  flex-wrap:wrap;
  gap:.5rem;
  margin-bottom:.8rem;
}

input, select {
  flex:1;
  padding:.55rem;
  border:1px solid var(--border);
  border-radius:6px;
  font-size:.95rem;
}

button {
  padding:.55rem 1rem;
  border:none;
  border-radius:6px;
  background:var(--primary);
  color:white;
  font-size:.95rem;
  cursor:pointer;
}

button.success { background:var(--success); }
button.danger { background:var(--danger); }

ul {
  list-style:none;
  padding:0;
  margin:0;
}

li {
  padding:.5rem 0;
  border-bottom:1px solid var(--border);
  font-size:.9rem;
}

li:last-child { border-bottom:none; }

.muted { color:var(--muted); }
.in { color:var(--success); font-weight:600; }
.out { color:var(--danger); font-weight:600; }

.badge {
  display:inline-block;
  padding:.2rem .5rem;
  border-radius:12px;
  font-size:.75rem;
  background:#eee;
}
</style>
</head>

<body>

<header>
  <h1>📦 Sistema de Inventario</h1>
</header>

<div class="container">

<div class="section">
<h3>➕ Entrada de stock</h3>
<form method="post" action="/inventory/entry">
<select name="product_id">
{% for p in productos %}
<option value="{{ p[0] }}">{{ p[1] }}</option>
{% endfor %}
</select>

<select name="supplier_id">
<option value="">Proveedor (opcional)</option>
{% for s in proveedores %}
<option value="{{ s[0] }}">{{ s[1] }}</option>
{% endfor %}
</select>

<input type="number" name="quantity" placeholder="Cantidad" required>
<button class="success">Agregar</button>
</form>
</div>

<div class="grid grid-2">

<div class="section">
<h3>Proveedores</h3>
<form method="post" action="/suppliers/create">
<input name="name" placeholder="Nuevo proveedor" required>
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
<input name="name" placeholder="Nuevo cliente" required>
<button>Crear</button>
</form>
<ul>
{% for c in clientes %}
<li>{{ c[1] }}</li>
{% endfor %}
</ul>
</div>

</div>

<div class="section">
<h3>Productos</h3>
<ul>
{% for p in productos %}
<li>
<strong>{{ p[1] }}</strong>
<span class="badge">{{ p[3] }}</span>
— Stock: {{ p[2] }}
</li>
{% endfor %}
</ul>
</div>

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
<strong>Pedido #{{ p[0] }}</strong>
<span class="muted">— {{ p[1] }}</span>

<form method="post" action="/orders/{{ p[0] }}/items/create">
<select name="product_id">
{% for prod in productos %}
<option value="{{ prod[0] }}">{{ prod[1] }}</option>
{% endfor %}
</select>
<input type="number" name="quantity" placeholder="Cantidad" required>
<button>Agregar</button>
</form>

<form method="post" action="/orders/{{ p[0] }}/confirm">
<button>Confirmar</button>
</form>
</li>
{% endfor %}
</ul>
</div>

<div class="section">
<h3>📊 Últimos movimientos</h3>
<ul>
{% for m in movimientos %}
<li>
<strong>{{ m[1] }}</strong>
<span class="badge">{{ m[2] }}</span>
—
<span class="{{ 'in' if m[3]=='entrada' else 'out' }}">{{ m[3] }}</span>
|
{{ m[4] }}
{% if m[6] %}
| {{ m[6] }}
{% endif %}
<br>
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

    @app.route("/suppliers/create", methods=["POST"])
    def crear_proveedor():
        query("INSERT INTO suppliers (name) VALUES (?)", (request.form["name"],))
        return redirect("/")

    @app.route("/clients/create", methods=["POST"])
    def crear_cliente():
        query("INSERT INTO clients (name) VALUES (?)", (request.form["name"],))
        return redirect("/")

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
