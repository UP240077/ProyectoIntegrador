from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import json
import os
from datetime import datetime

titulo_sistema = "SisVentas - Version Final"

app = Flask(__name__)
app.secret_key = "1234"  # cámbialo en producción

# -------------------------------------------------
# CARGAR ARCHIVOS DE IDIOMA
# -------------------------------------------------
def cargar_idioma(lang: str) -> dict:
    ruta = os.path.join("translations", f"{lang}.json")
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

IDIOMAS = {
    "es": cargar_idioma("es"),
    "en": cargar_idioma("en")
}

def t(key: str) -> str:
    lang = session.get("lang", "es")
    return IDIOMAS.get(lang, IDIOMAS["es"]).get(key, key)

app.jinja_env.globals.update(t=t)

# -------------------------------------------------
# CONEXIÓN A BD
# -------------------------------------------------
def conexion():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/ventas.db")
    return conn

# -------------------------------------------------
# CAMBIAR IDIOMA
# -------------------------------------------------
@app.route("/cambiar_idioma")
def cambiar_idioma():
    lang_actual = session.get("lang", "es")
    session["lang"] = "en" if lang_actual == "es" else "es"
    flash(t("language_changed"))
    return redirect(request.referrer or url_for("configuracion"))

# -------------------------------------------------
# DECORADOR: LOGIN REQUERIDO
# -------------------------------------------------
def login_requerido(func):
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            flash("🔐 Inicia sesión para continuar")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# -------------------------------------------------
# PÁGINA PRINCIPAL
# -------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------------------------------------
# PRODUCTOS
# -------------------------------------------------
@app.route("/productos")
@login_requerido
def productos():
    conn = conexion()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, categoria, precio, cantidad FROM productos")
    datos = cur.fetchall()
    conn.close()
    return render_template("productos.html", productos=datos)

@app.route("/nuevo_producto", methods=["GET", "POST"])
@login_requerido
def nuevo_producto():
    if request.method == "POST":
        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        precio = float(request.form["precio"])
        cantidad = int(request.form["cantidad"])

        conn = conexion()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO productos(nombre, categoria, precio, cantidad) VALUES (?, ?, ?, ?)",
            (nombre, categoria, precio, cantidad)
        )
        conn.commit()
        conn.close()

        flash(t("producto_agregado"))
        return redirect(url_for("productos"))

    return render_template("nuevo_producto.html")

@app.route("/eliminar_producto/<int:id>", methods=["POST"])
@login_requerido
def eliminar_producto(id):
    conn = conexion()
    cur = conn.cursor()
    cur.execute("DELETE FROM productos WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash(t("producto_eliminado"))
    return redirect(url_for("productos"))

# -------------------------------------------------
# VENTAS (COMPRAS)
# -------------------------------------------------
@app.route("/ventas", methods=["GET", "POST"])
@login_requerido
def ventas():
    conn = conexion()
    cur = conn.cursor()

    if request.method == "POST":
        descripcion = request.form["descripcion"]
        total = float(request.form["total"])
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.execute(
            "INSERT INTO ventas(descripcion, total, fecha) VALUES (?, ?, ?)",
            (descripcion, total, fecha)
        )
        conn.commit()
        flash(t("compra_registrada"))

    cur.execute("SELECT id, descripcion, total, fecha FROM ventas ORDER BY fecha DESC")
    datos = cur.fetchall()
    conn.close()
    return render_template("ventas.html", ventas=datos)

@app.route("/eliminar_venta/<int:id>", methods=["POST"])
@login_requerido
def eliminar_venta(id):
    conn = conexion()
    cur = conn.cursor()
    cur.execute("DELETE FROM ventas WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash(t("compra_eliminada"))
    return redirect(url_for("ventas"))

# -------------------------------------------------
# REPORTES
# -------------------------------------------------
@app.route("/reportes")
@login_requerido
def reportes():
    conn = conexion()
    cur = conn.cursor()
    cur.execute("SELECT id, tipo, descripcion, fecha FROM reportes ORDER BY fecha DESC")
    datos = cur.fetchall()
    conn.close()
    return render_template("reportes.html", reportes=datos)

@app.route("/nuevo_reporte", methods=["GET", "POST"])
@login_requerido
def nuevo_reporte():
    if request.method == "POST":
        tipo = request.form["tipo"]
        descripcion = request.form["descripcion"]
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = conexion()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO reportes(tipo, descripcion, fecha) VALUES (?, ?, ?)",
            (tipo, descripcion, fecha)
        )
        conn.commit()
        conn.close()
        flash(t("reporte_creado"))
        return redirect(url_for("reportes"))

    return render_template("nuevo_reporte.html")

@app.route("/eliminar_reporte/<int:id>", methods=["POST"])
@login_requerido
def eliminar_reporte(id):
    conn = conexion()
    cur = conn.cursor()
    cur.execute("DELETE FROM reportes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash(t("reporte_eliminado"))
    return redirect(url_for("reportes"))

# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------
@app.route("/configuracion")
@login_requerido
def configuracion():
    return render_template("configuracion.html")

# -------------------------------------------------
# USUARIOS: REGISTRO / LOGIN / LOGOUT
# -------------------------------------------------
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]

        conn = conexion()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO usuarios(nombre, correo, password) VALUES (?, ?, ?)",
                (nombre, correo, password)
            )
            conn.commit()
            flash(t("register_success"))
            return redirect(url_for("login"))
        except:
            flash(t("register_error_taken"))
        finally:
            conn.close()

    return render_template("registro.html")
@app.route("/cambiar_nombre", methods=["GET", "POST"])
@login_requerido
def cambiar_nombre():
    if request.method == "POST":
        nuevo_nombre = request.form["nombre"]

        conn = conexion()
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET nombre=? WHERE id=?", (nuevo_nombre, session["usuario_id"]))
        conn.commit()
        conn.close()

        session["usuario_nombre"] = nuevo_nombre
        flash("✅ Nombre actualizado correctamente")
        return redirect(url_for("configuracion"))

    return render_template("cambiar_nombre.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]

        conn = conexion()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, nombre FROM usuarios WHERE correo=? AND password=?",
            (correo, password)
        )
        usuario = cur.fetchone()
        conn.close()

        if usuario:
            session["usuario_id"] = usuario[0]
            session["usuario_nombre"] = usuario[1]
            flash(f"👋 {usuario[1]}")
            return redirect(url_for("index"))
        else:
            flash(t("login_error"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash(t("logout_success"))
    return redirect(url_for("login"))

# -------------------------------------------------
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)

# Cambio desde feature/productos para generar PR
