import json

# ============================================
# GASTOS FIJOS
# ============================================

# Monto mensual del plan de celular
gasto_celular = 250000

# Monto mensual del pago al papá
pago_papa = 100000

# ============================================
# CLASE INGRESO
# ============================================

class Ingreso:
    """
    Representa un ingreso de dinero.

    Atributos:
        fecha (str): Fecha del ingreso (ej. '2025-06-30')
        monto (float): Monto del ingreso
        nota (str): Descripción o comentario sobre el ingreso
    """
    def __init__(self, fecha, monto, nota):
        self.fecha = fecha
        self.monto = monto
        self.nota = nota

    def __str__(self):
        return f"Fecha: {self.fecha}, Monto: ${self.monto:,.2f}, Nota: {self.nota}"

# ============================================
# CLASE GASTO
# ============================================

class Gasto:
    """
    Representa un gasto de dinero.

    Atributos:
        fecha (str): Fecha del gasto (ej. '2025-06-30')
        monto (float): Monto del gasto
        nota (str): Descripción o comentario sobre el gasto
    """
    def __init__(self, fecha, monto, nota):
        self.fecha = fecha
        self.monto = monto
        self.nota = nota

    def __str__(self):
        return f"Fecha: {self.fecha}, Monto: ${self.monto:,.2f}, Nota: {self.nota}"

# ============================================
# FUNCIONES PARA GESTIONAR INGRESOS
# ============================================

def cargar_ingresos(archivo):
    """
    Carga la lista de ingresos desde un archivo JSON.

    Args:
        archivo (str): Nombre del archivo JSON.

    Returns:
        list: Lista de objetos Ingreso.
    """
    lista = []
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                ingreso = Ingreso(item["fecha"], item["monto"], item["nota"])
                lista.append(ingreso)
    except FileNotFoundError:
        # Si el archivo no existe aún, se devuelve una lista vacía
        print("⚠️ No se encontró archivo de ingresos. Se creará uno nuevo.")
    
    return lista


def agregar_ingreso(lista):
    """
    Solicita datos al usuario para crear un nuevo ingreso
    y lo agrega a la lista.

    Args:
        lista (list): Lista actual de ingresos.
    """
    print("\n========== AGREGAR INGRESO ==========")
    fecha = input("Ingrese la fecha del ingreso (ej. 2025-06-30): ")

    while True:
        try:
            monto = float(input("Ingrese el monto del ingreso: "))
            break
        except ValueError:
            print("¡Error! Debe ingresar un número válido.")

    nota = input("Agregue una nota o comentario para este ingreso: ")

    nuevo_ingreso = Ingreso(fecha, monto, nota)
    lista.append(nuevo_ingreso)
    print("✅ ¡Ingreso agregado correctamente!\n")


def mostrar_ingresos(lista):
    """
    Muestra en pantalla todos los ingresos registrados.

    Args:
        lista (list): Lista de ingresos.
    """
    if not lista:
        print("\n⚠️ No hay ingresos registrados.\n")
    else:
        print("\n========== LISTA DE INGRESOS ==========")
        for idx, ingreso in enumerate(lista, start=1):
            print(f"{idx}. {ingreso}")
        print("")  # línea en blanco al final


def total_ingresos(lista):
    """
    Calcula y muestra el total acumulado de los ingresos.

    Args:
        lista (list): Lista de ingresos.
    """
    total = 0
    for ingreso in lista:
        total += ingreso.monto

    print(f"El total de tus ingresos es de: ${total:,.2f}")


def guardar_ingreso(lista, archivo):
    """
    Guarda la lista de ingresos en un archivo JSON.

    Args:
        lista (list): Lista de ingresos.
        archivo (str): Nombre del archivo JSON.
    """
    data = []
    for ingreso in lista:
        data.append({
            "fecha": ingreso.fecha,
            "monto": ingreso.monto,
            "nota": ingreso.nota
        })
    
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    
    print("✅ Ingreso agregado exitosamente.")




# ============================================
# FUNCIONES PARA GESTIONAR GASTOS
# ============================================

def cargar_gastos(archivo):
    """
    Carga la lista de gastos desde un archivo JSON.

    Args:
        archivo (str): Nombre del archivo JSON.

    Returns:
        list: Lista de objetos Gasto.
    """
    lista = []
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                gasto = Gasto(item["fecha"], item["monto"], item["nota"])
                lista.append(gasto)
    except FileNotFoundError:
        # Si el archivo no existe aún, se devuelve una lista vacía
        print("⚠️ No se encontró archivo de gastos. Se creará uno nuevo.")
    
    return lista


def agregar_gastos(lista):
    """
    Solicita datos al usuario para crear un nuevo gasto
    y lo agrega a la lista.

    Args:
        lista (list): Lista actual de gastos.
    """
    print("\n========== AGREGAR GASTO ==========")
    fecha = input("Ingrese la fecha del gasto (ej. 2025-06-30): ")

    while True:
        try:
            monto = float(input("Ingrese el monto del gasto: "))
            break
        except ValueError:
            print("¡Error! Debe ingresar un número válido.")

    nota = input("Agregue una nota o comentario para este gasto: ")

    nuevo_gasto = Gasto(fecha, monto, nota)
    lista.append(nuevo_gasto)
    print("✅ ¡Gasto agregado correctamente!\n")


def mostrar_gastos(lista):
    """
    Muestra en pantalla todos los gastos registrados.

    Args:
        lista (list): Lista de gastos.
    """
    if not lista:
        print("\n⚠️ No hay gastos registrados.\n")
    else:
        print("\n========== LISTA DE GASTOS ==========")
        for idx, gasto in enumerate(lista, start=1):
            print(f"{idx}. {gasto}")
        print("")  # línea en blanco al final


def total_gastos(lista):
    """
    Calcula y muestra el total acumulado de los gastos.

    Args:
        lista (list): Lista de gastos.
    """
    total = 0
    for gasto in lista:
        total += gasto.monto

    print(f"El total de tus gastos es de: ${total:,.2f}")


def guardar_gastos(lista, archivo):
    """
    Guarda la lista de gastos en un archivo JSON.

    Args:
        lista (list): Lista de gastos.
        archivo (str): Nombre del archivo JSON.
    """
    data = []
    for gasto in lista:
        data.append({
            "fecha": gasto.fecha,
            "monto": gasto.monto,
            "nota": gasto.nota
        })
    
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    
    print("✅ Archivo de gastos guardado exitosamente.")


def calcular_saldo(lista_ingresos, lista_gastos):
    """
    Calcula y muestra el saldo disponible
    (ingresos totales menos gastos totales).

    Args:
        lista_ingresos (list): Lista de ingresos.
        lista_gastos (list): Lista de gastos.
    """
    total_ing = sum(item.monto for item in lista_ingresos)
    total_gast = sum(item.monto for item in lista_gastos)
    saldo = total_ing - total_gast

    print(f"\n========== SALDO DISPONIBLE ==========")
    print(f"Ingresos totales: ${total_ing:,.2f}")
    print(f"Gastos totales : ${total_gast:,.2f}")
    print(f"Saldo disponible: ${saldo:,.2f}\n")



# ============================================
# CARGAR LISTAS AL INICIAR
# ============================================

lista_ingresos = cargar_ingresos("ingresos.json")
lista_gastos = cargar_gastos("gastos.json")


# ============================================
# MENÚ PRINCIPAL
# ============================================

while True:
    print('''
========================================
               MENÚ PRINCIPAL
========================================
1. Agregar un nuevo ingreso
2. Agregar un nuevo gasto
3. Mostrar ingresos registrados
4. Mostrar gastos registrados
5. Mostrar total de ingresos
6. Mostrar total de gastos
7. Mostrar saldo disponible
8. Salir del programa
''')

    try:
        opcion = int(input("Seleccione una opción (1-8): "))
    except ValueError:
        print("¡Error! Debe ingresar un número válido.\n")
        continue

    if opcion == 1:
        agregar_ingreso(lista_ingresos)

    elif opcion == 2:
        agregar_gastos(lista_gastos)

    elif opcion == 3:
        mostrar_ingresos(lista_ingresos)

    elif opcion == 4:
        mostrar_gastos(lista_gastos)

    elif opcion == 5:
        total_ingresos(lista_ingresos)

    elif opcion == 6:
        total_gastos(lista_gastos)

    elif opcion == 7:
        calcular_saldo(lista_ingresos, lista_gastos)

    elif opcion == 8:
        guardar_ingreso(lista_ingresos, "ingresos.json")
        guardar_gastos(lista_gastos, "gastos.json")
        print("\nGracias por usar el sistema. ¡Hasta pronto!")
        break


    else:
        print("⚠️ Opción inválida. Por favor, intente nuevamente.\n")
