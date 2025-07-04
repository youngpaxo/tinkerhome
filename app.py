from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import psutil
from flask import jsonify
import psutil
import platform
import time
import datetime
import socket
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response


# =========================================================
# GASTOS FIJOS
# =========================================================

gasto_celular = 125000
universidad = 50000
pago_papa = 100000
ahorros = 50000

saldo_inicial = 497991
efectivo = 15000

# =========================================================
# CLASES
# =========================================================

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Ingreso:
    def __init__(self, id, fecha, monto, nota, cuenta):
        self.id = id
        self.fecha = fecha
        self.monto = monto
        self.nota = nota
        self.cuenta = cuenta

class Gasto:
    def __init__(self, id, fecha, monto, nota, cuenta):
        self.id = id
        self.fecha = fecha
        self.monto = monto
        self.nota = nota
        self.cuenta = cuenta

class Cuenta:
    def __init__(self, nombre, monto):
        self.nombre = nombre
        self.monto = monto

class Notas:
    def __init__(self, id, fecha, nota):
        self.id = id
        self.fecha = fecha
        self.nota = nota

# =========================================================
# FUNCIONES
# =========================================================

def cargar_usuarios(archivo):
    usuarios = []
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                usuarios.append(User(
                    item["id"],
                    item["username"],
                    item["password_hash"]
                ))
    return usuarios

def guardar_usuarios(lista, archivo):
    data = []
    for user in lista:
        data.append({
            "id": user.id,
            "username": user.username,
            "password_hash": user.password_hash
        })
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)



def cargar_ingresos(archivo):
    lista = []
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                lista.append(Ingreso(
                    item["id"],
                    item["fecha"],
                    item["monto"],
                    item["nota"],
                    item.get("cuenta", "efectivo")
                ))
    return lista

def cargar_gastos(archivo):
    lista = []
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                lista.append(Gasto(
                    item["id"],
                    item["fecha"],
                    item["monto"],
                    item["nota"],
                    item.get("cuenta", "efectivo")
                ))
    return lista

def guardar_ingresos(lista, archivo):
    data = []
    for ingreso in lista:
        data.append({
            "id": ingreso.id,
            "fecha": ingreso.fecha,
            "monto": ingreso.monto,
            "nota": ingreso.nota,
            "cuenta": ingreso.cuenta
        })
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def guardar_gastos(lista, archivo):
    data = []
    for gasto in lista:
        data.append({
            "id": gasto.id,
            "fecha": gasto.fecha,
            "monto": gasto.monto,
            "nota": gasto.nota,
            "cuenta": gasto.cuenta
        })
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def calcular_total(lista):
    return sum(item.monto for item in lista)

def generar_id(lista):
    if not lista:
        return 1
    else:
        max_id = max(item.id for item in lista)
        return max_id + 1

def cargar_nota(archivo):
    lista = []
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                lista.append(Notas(
                    item["id"],
                    item["fecha"],
                    item["nota"]
                ))
    return lista

def guardar_nota(lista, archivo):
    data = []
    for nota in lista:
        data.append({
            "id": nota.id,
            "fecha": nota.fecha,
            "nota": nota.nota
        })
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# =========================================================
# FLASK
# =========================================================

app = Flask(__name__)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

usuarios = cargar_usuarios("users.json")

@login_manager.user_loader
def load_user(user_id):
    return next((u for u in usuarios if str(u.id) == str(user_id)), None)


@app.route("/")
@login_required
def index():
    ingresos = cargar_ingresos("ingresos.json")
    gastos = cargar_gastos("gastos.json")
    notas = cargar_nota("notas.json")

    total_ingresos = calcular_total(ingresos)
    total_gastos = calcular_total(gastos)
    saldo_neto = total_ingresos - total_gastos
    total_notas = len(notas)

    proximo_partido = "U. de Chile vs Colo Colo - Domingo 16:30"

    response = make_response(render_template(
        "vps.html",
        total_ingresos=total_ingresos,
        total_gastos=total_gastos,
        saldo_neto=saldo_neto,
        total_notas=total_notas,
        proximo_partido=proximo_partido,
    ))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


@app.route("/ingresos", methods=["GET", "POST"])
def ingresos():
    if request.method == "POST":
        fecha = request.form["fecha"]
        monto = float(request.form["monto"])
        nota = request.form["nota"]
        cuenta = request.form["cuenta"]

        lista = cargar_ingresos("ingresos.json")
        nuevo_id = generar_id(lista)
        nuevo_ingreso = Ingreso(nuevo_id, fecha, monto, nota, cuenta)
        lista.append(nuevo_ingreso)
        guardar_ingresos(lista, "ingresos.json")

        return redirect(url_for("ingresos"))

    lista = cargar_ingresos("ingresos.json")
    total = calcular_total(lista)
    return render_template("ingresos.html", ingresos=lista, total=total)

@app.route("/editar_ingreso/<int:id>", methods=["GET", "POST"])
def editar_ingreso(id):
    lista = cargar_ingresos("ingresos.json")
    ingreso = next((i for i in lista if i.id == id), None)
    if ingreso is None:
        return "Ingreso no encontrado", 404

    if request.method == "POST":
        ingreso.fecha = request.form["fecha"]
        ingreso.monto = float(request.form["monto"])
        ingreso.nota = request.form["nota"]
        ingreso.cuenta = request.form["cuenta"]
        guardar_ingresos(lista, "ingresos.json")
        return redirect(url_for("ingresos"))

    return render_template("editar_ingreso.html", ingreso=ingreso)

@app.route("/ver_ingreso/<int:id>")
def ver_ingreso(id):
    lista = cargar_ingresos("ingresos.json")
    ingreso = next((i for i in lista if i.id == id), None)
    if ingreso is None:
        return "Ingreso no encontrado", 404
    return render_template("ver_ingreso.html", ingreso=ingreso)

@app.route("/borrar_ingreso/<int:id>", methods=["POST"])
def borrar_ingreso(id):
    lista = cargar_ingresos("ingresos.json")
    lista = [i for i in lista if i.id != id]
    guardar_ingresos(lista, "ingresos.json")
    return redirect(url_for("ingresos"))

@app.route("/gastos", methods=["GET", "POST"])
def gastos():
    if request.method == "POST":
        fecha = request.form["fecha"]
        monto = float(request.form["monto"])
        nota = request.form["nota"]
        cuenta = request.form["cuenta"]

        lista = cargar_gastos("gastos.json")
        nuevo_id = generar_id(lista)
        nuevo_gasto = Gasto(nuevo_id, fecha, monto, nota, cuenta)
        lista.append(nuevo_gasto)
        guardar_gastos(lista, "gastos.json")

        return redirect(url_for("gastos"))

    lista = cargar_gastos("gastos.json")
    total = calcular_total(lista)
    return render_template("gastos.html", gastos=lista, total=total)

@app.route("/notas", methods=["GET", "POST"])
def notas():
    if request.method == "POST":
        fecha = request.form["fecha"]
        nota_texto = request.form["nota"]

        lista = cargar_nota("notas.json")
        nuevo_id = generar_id(lista)
        nueva_nota = Notas(nuevo_id, fecha, nota_texto)
        lista.append(nueva_nota)
        guardar_nota(lista, "notas.json")

        return redirect(url_for("notas"))

    lista = cargar_nota("notas.json")
    return render_template("notas.html", notas=lista)

@app.route("/stats")
def vps():
    return render_template("stats.html")

@app.route("/api/vps")
def api_vps():
    # CPU total y por núcleo
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
    cpu_freq = psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
    cpu_times = psutil.cpu_times()._asdict()
    logical_cpus = psutil.cpu_count(logical=True)
    physical_cpus = psutil.cpu_count(logical=False)

    # Load average (solo UNIX)
    load_avg = None
    if hasattr(os, "getloadavg"):
        la = os.getloadavg()
        load_avg = {
            "1min": la[0],
            "5min": la[1],
            "15min": la[2]
        }

    # RAM
    mem = psutil.virtual_memory()
    ram_info = {
        "total": mem.total,
        "used": mem.used,
        "available": mem.available,
        "percent": mem.percent
    }

    # SWAP
    swap = psutil.swap_memory()
    swap_info = {
        "total": swap.total,
        "used": swap.used,
        "percent": swap.percent
    }

    # Disk partitions
    partitions_info = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        partitions_info.append({
            "device": part.device,
            "mountpoint": part.mountpoint,
            "fstype": part.fstype,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent
        })

    # Disk I/O
    disk_io = psutil.disk_io_counters()._asdict()

    # Network I/O totals
    net_io = psutil.net_io_counters()._asdict()

    # Network interfaces info
    net_if_stats = {iface: stats._asdict() for iface, stats in psutil.net_if_stats().items()}
    net_if_addrs = {
        iface: [addr.address for addr in addrs if addr.family == socket.AF_INET]
        for iface, addrs in psutil.net_if_addrs().items()
    }

    # Users
    users_list = []
    for u in psutil.users():
        users_list.append({
            "name": u.name,
            "terminal": u.terminal,
            "host": u.host,
            "started": datetime.datetime.fromtimestamp(u.started).strftime("%Y-%m-%d %H:%M:%S")
        })

    # Processes
    processes = []
    for proc in psutil.process_iter(attrs=["pid", "name", "username", "cpu_percent", "memory_percent", "status", "create_time"]):
        try:
            info = proc.info
            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "username": info["username"],
                "cpu_percent": info["cpu_percent"],
                "memory_percent": info["memory_percent"],
                "status": info["status"],
                "created": datetime.datetime.fromtimestamp(info["create_time"]).strftime("%Y-%m-%d %H:%M:%S")
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # System info
    uname = platform.uname()
    system_info = {
        "system": uname.system,
        "node": uname.node,
        "release": uname.release,
        "version": uname.version,
        "machine": uname.machine,
        "processor": uname.processor,
        "python_version": platform.python_version()
    }

    # Distro info (solo Linux)
    try:
        import distro
        distro_info = {
            "name": distro.name(),
            "version": distro.version(),
            "id": distro.id()
        }
    except ImportError:
        distro_info = None

    # Boot time
    boot_timestamp = psutil.boot_time()
    boot_time_str = datetime.datetime.fromtimestamp(boot_timestamp).strftime("%Y-%m-%d %H:%M:%S")

    # Opcional → Puertos abiertos (esto puede tardar)
    open_ports = []
    try:
        for conn in psutil.net_connections(kind="inet"):
            if conn.status == "LISTEN":
                open_ports.append({
                    "ip": conn.laddr.ip,
                    "port": conn.laddr.port,
                    "pid": conn.pid
                })
    except Exception:
        pass

    return jsonify({
        "cpu_percent": cpu_percent,
        "cpu_per_core": cpu_per_core,
        "cpu_freq": cpu_freq,
        "cpu_times": cpu_times,
        "logical_cpus": logical_cpus,
        "physical_cpus": physical_cpus,
        "load_average": load_avg,
        "ram_info": ram_info,
        "swap_info": swap_info,
        "disk_partitions": partitions_info,
        "disk_io": disk_io,
        "net_io": net_io,
        "net_if_stats": net_if_stats,
        "net_if_addrs": net_if_addrs,
        "users_logged_in": users_list,
        "processes": processes,
        "system_info": system_info,
        "distro_info": distro_info,
        "boot_time": boot_time_str,
        "open_ports": open_ports
    })


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = next((u for u in usuarios if u.username == username), None)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            return "Usuario o contraseña incorrectos.", 401

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
     


app.secret_key = "superclaveultrasecreta123"