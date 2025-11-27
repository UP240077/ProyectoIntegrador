import sqlite3, os

os.makedirs("data", exist_ok=True)

conn = sqlite3.connect("data/ventas.db")
cursor = conn.cursor()

# Tabla productos
cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio REAL NOT NULL,
    cantidad INTEGER NOT NULL
)
""")

# Tabla ventas (compras)
cursor.execute("""
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion TEXT NOT NULL,
    total REAL NOT NULL,
    fecha TEXT NOT NULL
)
""")

# Tabla reportes
cursor.execute("""
CREATE TABLE IF NOT EXISTS reportes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    fecha TEXT NOT NULL
)
""")

# Tabla usuarios (para login/registro)
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("✅ Base de datos lista (productos, ventas, reportes, usuarios)")
