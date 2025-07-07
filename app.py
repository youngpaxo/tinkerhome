from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import datetime
import os

# -------------------------------------------------------
# Configuración Flask
# -------------------------------------------------------

app = Flask(__name__)
app.secret_key = "superclaveultrasecreta123"

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# -------------------------------------------------------
# Base de datos SQLite
# -------------------------------------------------------

DB_NAME = "finanzas.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password_hash TEXT,
                created_at TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                fecha TEXT,
                tipo TEXT,
                categoria TEXT,
                monto REAL,
                cuenta TEXT,
                nota TEXT,
                descripcion TEXT,
                meta_asociada TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                fecha TEXT,
                nota TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)

init_db()

# -------------------------------------------------------
# Clases
# -------------------------------------------------------

class User(UserMixin):
    def __init__(self, id, username, password_hash, created_at):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.created_at = None
        if created_at:
            self.created_at = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# -------------------------------------------------------
# User Loader
# -------------------------------------------------------

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, password_hash, created_at
            FROM users
            WHERE id = ?
        """, (user_id,))
        row = cursor.fetchone()

    if row:
        return User(
            row["id"],
            row["username"],
            row["password_hash"],
            row["created_at"]
        )
    return None


# -------------------------------------------------------
# FUNCIONES REUTILIZABLES
# -------------------------------------------------------

def ultimos_movimientos(user_id, tipo, limite=5):
    """
    Devuelve los últimos movimientos (ingresos o gastos) ordenados por fecha.
    """
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fecha, monto, nota
            FROM movimientos
            WHERE user_id = ? AND tipo = ?
            ORDER BY fecha DESC
            LIMIT ?
        """, (user_id, tipo, limite))
        rows = cursor.fetchall()

    return rows


def calcular_totales(user_id):
    """
    Devuelve totales de ingresos, gastos, ahorros y saldo neto.
    """
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT tipo, SUM(monto) as total
            FROM movimientos
            WHERE user_id = ?
            GROUP BY tipo
        """, (user_id,))
        rows = cursor.fetchall()

    total_ingresos = sum(r["total"] for r in rows if r["tipo"] == "Ingreso")
    total_gastos = sum(r["total"] for r in rows if r["tipo"] == "Gasto")
    total_ahorros = sum(r["total"] for r in rows if r["tipo"] == "Ahorro")

    saldo_neto = (total_ingresos or 0) - (total_gastos or 0) - (total_ahorros or 0)

    return {
        "total_ingresos": total_ingresos or 0,
        "total_gastos": total_gastos or 0,
        "total_ahorros": total_ahorros or 0,
        "saldo_neto": saldo_neto
    }

def totales_por_categoria(user_id, tipo=None):
    """
    Devuelve totales agrupados por categoría.
    """
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        sql = """
            SELECT categoria, SUM(monto) as total
            FROM movimientos
            WHERE user_id = ?
        """
        params = [user_id]

        if tipo:
            sql += " AND tipo = ?"
            params.append(tipo)

        sql += " GROUP BY categoria ORDER BY total DESC"

        cursor.execute(sql, params)
        rows = cursor.fetchall()

    return rows

def totales_diarios(user_id, tipo=None):
    """
    Devuelve suma de movimientos agrupados por fecha.
    Útil para gráficas diarias.
    """
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        sql = """
            SELECT fecha, SUM(monto) as total
            FROM movimientos
            WHERE user_id = ?
        """
        params = [user_id]

        if tipo:
            sql += " AND tipo = ?"
            params.append(tipo)

        sql += " GROUP BY fecha ORDER BY fecha ASC"

        cursor.execute(sql, params)
        rows = cursor.fetchall()

    return rows

def totales_mensuales(user_id, tipo=None):
    """
    Devuelve suma de movimientos agrupados por mes (YYYY-MM).
    """
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        sql = """
            SELECT substr(fecha, 1, 7) as mes, SUM(monto) as total
            FROM movimientos
            WHERE user_id = ?
        """
        params = [user_id]

        if tipo:
            sql += " AND tipo = ?"
            params.append(tipo)

        sql += " GROUP BY mes ORDER BY mes ASC"

        cursor.execute(sql, params)
        rows = cursor.fetchall()

    return rows

def listar_cuentas(user_id):
    """
    Devuelve lista de cuentas usadas.
    """
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT cuenta
            FROM movimientos
            WHERE user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()

    return [r["cuenta"] for r in rows]

def saldo_por_cuenta(user_id):
    """
    Devuelve saldo total por cuenta.
    """
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT cuenta,
                   SUM(CASE WHEN tipo='Ingreso' THEN monto ELSE 0 END) -
                   SUM(CASE WHEN tipo='Gasto' THEN monto ELSE 0 END) as saldo
            FROM movimientos
            WHERE user_id = ?
            GROUP BY cuenta
        """, (user_id,))
        rows = cursor.fetchall()

    return rows

def listar_metas(user_id):
    """
    Devuelve metas únicas registradas en movimientos.
    """
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT meta_asociada
            FROM movimientos
            WHERE user_id = ? AND meta_asociada != ''
        """, (user_id,))
        rows = cursor.fetchall()

    return [r["meta_asociada"] for r in rows]

def top_categorias(user_id, limite=5):
    """
    Devuelve top categorías con mayor gasto.
    """
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT categoria, SUM(monto) as total
            FROM movimientos
            WHERE user_id = ? AND tipo = 'Gasto'
            GROUP BY categoria
            ORDER BY total DESC
            LIMIT ?
        """, (user_id, limite))
        rows = cursor.fetchall()

    return rows

# -------------------------------------------------------
# RUTAS
# -------------------------------------------------------

@app.route("/")
@login_required
def index():
    totales = calcular_totales(current_user.id)

    ultimos_ingresos = ultimos_movimientos(current_user.id, "Ingreso", limite=5)
    ultimos_gastos = ultimos_movimientos(current_user.id, "Gasto", limite=5)

    return render_template(
        "index.html",
        ultimos_ingresos=ultimos_ingresos,
        ultimos_gastos=ultimos_gastos,
        **totales
    )


@app.route("/movimientos", methods=["GET", "POST"])
@login_required
def movimientos():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if request.method == "POST":
            fecha = request.form["fecha"]
            tipo = request.form["tipo"]
            categoria = request.form["categoria"]
            monto = float(request.form["monto"])
            cuenta = request.form["cuenta"]
            nota = request.form.get("nota", "")
            descripcion = request.form.get("descripcion", "")
            meta_asociada = request.form.get("meta_asociada", "")

            cursor.execute("""
                INSERT INTO movimientos (
                    user_id, fecha, tipo, categoria, monto,
                    cuenta, nota, descripcion, meta_asociada
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                current_user.id,
                fecha,
                tipo,
                categoria,
                monto,
                cuenta,
                nota,
                descripcion,
                meta_asociada
            ))
            conn.commit()
            return redirect(url_for("movimientos"))

        filtro_tipo = request.args.get("tipo")

        if filtro_tipo:
            cursor.execute("""
                SELECT *
                FROM movimientos
                WHERE user_id = ? AND tipo = ?
                ORDER BY fecha DESC
            """, (current_user.id, filtro_tipo))
        else:
            cursor.execute("""
                SELECT *
                FROM movimientos
                WHERE user_id = ?
                ORDER BY fecha DESC
            """, (current_user.id,))
        
        rows = cursor.fetchall()

        # Convertir monto a float
        movimientos = []
        for row in rows:
            movimientos.append((
                row["id"],
                row["user_id"],
                row["fecha"],
                row["tipo"],
                float(row["monto"]),
                row["cuenta"],
                row["nota"],
                row["descripcion"],
                row["meta_asociada"]
            ))

    totales = calcular_totales(current_user.id)
    categorias = totales_por_categoria(current_user.id)
    cuentas = listar_cuentas(current_user.id)
    metas = listar_metas(current_user.id)

    return render_template(
        "movimientos.html",
        movimientos=movimientos,
        filtro_tipo=filtro_tipo,
        categorias=categorias,
        cuentas=cuentas,
        metas=metas,
        **totales
    )


@app.route("/borrar_movimiento/<int:id>", methods=["POST"])
@login_required
def borrar_movimiento(id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM movimientos
            WHERE id = ? AND user_id = ?
        """, (id, current_user.id))
        conn.commit()
    return redirect(url_for("movimientos"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO users (username, password_hash, created_at)
                    VALUES (?, ?, ?)
                """, (username, hashed_password, created_at))
                conn.commit()
            except sqlite3.IntegrityError:
                return "El usuario ya existe."

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, password_hash, created_at FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()

        if row:
            user = User(
                row["id"],
                row["username"],
                row["password_hash"],
                row["created_at"]
            )

            if user.check_password(password):
                login_user(user)
                return redirect(url_for("index"))

        # Si row es None o la contraseña está mal:
        return "Usuario o contraseña incorrectos."

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/perfil")
@login_required
def perfil():
    return render_template("perfil.html")

@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")

@app.route("/vps")
@login_required
def vps():
    return render_template("vps.html")

@app.route("/notas", methods=["GET", "POST"])
@login_required
def notas():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if request.method == "POST":
            fecha = request.form["fecha"]
            nota_texto = request.form["nota"]

            cursor.execute("""
                INSERT INTO notas (user_id, fecha, nota)
                VALUES (?, ?, ?)
            """, (current_user.id, fecha, nota_texto))
            conn.commit()
            return redirect(url_for("notas"))

        cursor.execute("""
            SELECT id, fecha, nota
            FROM notas
            WHERE user_id = ?
            ORDER BY fecha DESC
        """, (current_user.id,))
        rows = cursor.fetchall()

    return render_template("notas.html", notas=rows)

# -------------------------------------------------------
# App run
# -------------------------------------------------------

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
    