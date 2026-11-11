# =============================================================
# main.py
# Punto de entrada del Sistema de Gestión de Pacientes CCSS
# Ejecutar con: python main.py
# =============================================================

import uuid
from datetime import datetime

import database
import crud


# =============================================================
# Funciones auxiliares de entrada
# =============================================================

def leer_uuid(mensaje):
    """
    Solicita al usuario un UUID y lo convierte al tipo correcto.
    Repite la solicitud si el formato es inválido.
    """
    while True:
        texto = input(mensaje).strip()
        try:
            return uuid.UUID(texto)
        except ValueError:
            print("✘ UUID inválido. Use el formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")


def leer_fecha(mensaje):
    """
    Solicita al usuario una fecha en formato YYYY-MM-DD.
    Retorna un objeto date o None si el usuario cancela.
    """
    while True:
        texto = input(mensaje).strip()
        if texto == "":
            return None
        try:
            return datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            print("✘ Fecha inválida. Use el formato: YYYY-MM-DD (ej. 1990-05-20)")


def leer_texto(mensaje):
    """Solicita un texto no vacío al usuario."""
    while True:
        texto = input(mensaje).strip()
        if texto:
            return texto
        print("✘ El campo no puede estar vacío.")


def pausar():
    """Pausa la ejecución hasta que el usuario presione Enter."""
    input("\nPresione Enter para continuar...")


# =============================================================
# Menú de pacientes
# =============================================================

def menu_registrar_paciente(session):
    print("\n--- Registrar paciente ---")
    nombre = leer_texto("Nombre: ")
    apellido = leer_texto("Apellido: ")
    fecha_nac = leer_fecha("Fecha de nacimiento (YYYY-MM-DD): ")
    if fecha_nac is None:
        print("✘ Operación cancelada.")
        return
    telefono = leer_texto("Teléfono: ")
    crud.crear_paciente(session, nombre, apellido, fecha_nac, telefono)


def menu_consultar_paciente(session):
    print("\n--- Consultar paciente ---")
    pid = leer_uuid("ID del paciente: ")
    fila = crud.obtener_paciente(session, pid)
    if fila:
        print(f"\n  ID:               {fila.paciente_id}")
        print(f"  Nombre:           {fila.nombre} {fila.apellido}")
        print(f"  Fecha nacimiento: {fila.fecha_nacimiento}")
        print(f"  Teléfono:         {fila.telefono}")
    else:
        print("✘ Paciente no encontrado.")


def menu_listar_pacientes(session):
    print("\n--- Lista de pacientes ---")
    filas = crud.listar_pacientes(session)
    if not filas:
        print("  No hay pacientes registrados.")
        return
    print(f"  {'ID':<38} {'Nombre':<20} {'Apellido':<20} {'Teléfono'}")
    print("  " + "-" * 90)
    for f in filas:
        print(f"  {str(f.paciente_id):<38} {f.nombre:<20} {f.apellido:<20} {f.telefono}")


def menu_actualizar_paciente(session):
    print("\n--- Actualizar teléfono de paciente ---")
    pid = leer_uuid("ID del paciente: ")
    nuevo_tel = leer_texto("Nuevo teléfono: ")
    crud.actualizar_telefono_paciente(session, pid, nuevo_tel)


def menu_eliminar_paciente(session):
    print("\n--- Eliminar paciente ---")
    pid = leer_uuid("ID del paciente: ")
    confirmacion = input("¿Está seguro? Se eliminarán todos sus registros médicos. (s/n): ").strip().lower()
    if confirmacion == "s":
        crud.eliminar_paciente(session, pid)
    else:
        print("Operación cancelada.")


# =============================================================
# Menú de consultas médicas
# =============================================================

def mostrar_consultas(session, pid):
    """Muestra las consultas de un paciente y retorna la lista."""
    filas = crud.listar_consultas(session, pid)
    if not filas:
        print("  No hay consultas registradas para este paciente.")
        return []
    print(f"\n  {'#':<3} {'Fecha':<25} {'Diagnóstico':<35} {'ID Consulta'}")
    print("  " + "-" * 100)
    for i, f in enumerate(filas, 1):
        fecha_str = f.fecha_consulta.strftime("%Y-%m-%d %H:%M")
        print(f"  {i:<3} {fecha_str:<25} {(f.diagnostico or '')[:33]:<35} {f.consulta_id}")
    return filas


def menu_consultas(session):
    while True:
        print("\n--- Gestión de consultas médicas ---")
        print("  1. Registrar consulta")
        print("  2. Ver historial de consultas")
        print("  3. Actualizar diagnóstico")
        print("  4. Eliminar consulta")
        print("  0. Volver al menú principal")
        opcion = input("Seleccione: ").strip()

        if opcion == "1":
            pid = leer_uuid("ID del paciente: ")
            diagnostico = leer_texto("Diagnóstico: ")
            observaciones = leer_texto("Observaciones: ")
            crud.registrar_consulta(session, pid, diagnostico, observaciones)
            pausar()

        elif opcion == "2":
            pid = leer_uuid("ID del paciente: ")
            mostrar_consultas(session, pid)
            pausar()

        elif opcion == "3":
            pid = leer_uuid("ID del paciente: ")
            filas = mostrar_consultas(session, pid)
            if filas:
                try:
                    num = int(input("Número de consulta a actualizar: ")) - 1
                    if 0 <= num < len(filas):
                        f = filas[num]
                        nuevo = leer_texto("Nuevo diagnóstico: ")
                        crud.actualizar_diagnostico(session, f.paciente_id, f.fecha_consulta, f.consulta_id, nuevo)
                    else:
                        print("✘ Número fuera de rango.")
                except ValueError:
                    print("✘ Ingrese un número válido.")
            pausar()

        elif opcion == "4":
            pid = leer_uuid("ID del paciente: ")
            filas = mostrar_consultas(session, pid)
            if filas:
                try:
                    num = int(input("Número de consulta a eliminar: ")) - 1
                    if 0 <= num < len(filas):
                        f = filas[num]
                        crud.eliminar_consulta(session, f.paciente_id, f.fecha_consulta, f.consulta_id)
                    else:
                        print("✘ Número fuera de rango.")
                except ValueError:
                    print("✘ Ingrese un número válido.")
            pausar()

        elif opcion == "0":
            break
        else:
            print("✘ Opción inválida.")


# =============================================================
# Menú de laboratorios
# =============================================================

def mostrar_laboratorios(session, pid):
    """Muestra los laboratorios de un paciente y retorna la lista."""
    filas = crud.listar_laboratorios(session, pid)
    if not filas:
        print("  No hay resultados de laboratorio para este paciente.")
        return []
    print(f"\n  {'#':<3} {'Fecha':<25} {'Tipo de examen':<30} {'Resultado'}")
    print("  " + "-" * 100)
    for i, f in enumerate(filas, 1):
        fecha_str = f.fecha_resultado.strftime("%Y-%m-%d %H:%M")
        print(f"  {i:<3} {fecha_str:<25} {(f.tipo_examen or '')[:28]:<30} {(f.resultado or '')[:40]}")
    return filas


def menu_laboratorios(session):
    while True:
        print("\n--- Gestión de laboratorios ---")
        print("  1. Registrar resultado")
        print("  2. Ver resultados por paciente")
        print("  3. Actualizar resultado")
        print("  4. Eliminar resultado")
        print("  0. Volver al menú principal")
        opcion = input("Seleccione: ").strip()

        if opcion == "1":
            pid = leer_uuid("ID del paciente: ")
            tipo = leer_texto("Tipo de examen: ")
            resultado = leer_texto("Resultado: ")
            crud.registrar_laboratorio(session, pid, tipo, resultado)
            pausar()

        elif opcion == "2":
            pid = leer_uuid("ID del paciente: ")
            mostrar_laboratorios(session, pid)
            pausar()

        elif opcion == "3":
            pid = leer_uuid("ID del paciente: ")
            filas = mostrar_laboratorios(session, pid)
            if filas:
                try:
                    num = int(input("Número de resultado a actualizar: ")) - 1
                    if 0 <= num < len(filas):
                        f = filas[num]
                        nuevo = leer_texto("Nuevo resultado: ")
                        crud.actualizar_resultado_laboratorio(
                            session, f.paciente_id, f.fecha_resultado, f.laboratorio_id, nuevo)
                    else:
                        print("✘ Número fuera de rango.")
                except ValueError:
                    print("✘ Ingrese un número válido.")
            pausar()

        elif opcion == "4":
            pid = leer_uuid("ID del paciente: ")
            filas = mostrar_laboratorios(session, pid)
            if filas:
                try:
                    num = int(input("Número de resultado a eliminar: ")) - 1
                    if 0 <= num < len(filas):
                        f = filas[num]
                        crud.eliminar_laboratorio(session, f.paciente_id, f.fecha_resultado, f.laboratorio_id)
                    else:
                        print("✘ Número fuera de rango.")
                except ValueError:
                    print("✘ Ingrese un número válido.")
            pausar()

        elif opcion == "0":
            break
        else:
            print("✘ Opción inválida.")


# =============================================================
# Menú de prescripciones
# =============================================================

def mostrar_prescripciones(session, pid):
    """Muestra las prescripciones de un paciente y retorna la lista."""
    filas = crud.listar_prescripciones(session, pid)
    if not filas:
        print("  No hay prescripciones para este paciente.")
        return []
    print(f"\n  {'#':<3} {'Fecha':<25} {'Medicamento':<25} {'Dosis'}")
    print("  " + "-" * 100)
    for i, f in enumerate(filas, 1):
        fecha_str = f.fecha_prescripcion.strftime("%Y-%m-%d %H:%M")
        print(f"  {i:<3} {fecha_str:<25} {(f.medicamento or '')[:23]:<25} {f.dosis or ''}")
    return filas


def menu_prescripciones(session):
    while True:
        print("\n--- Gestión de prescripciones ---")
        print("  1. Registrar prescripción")
        print("  2. Ver prescripciones por paciente")
        print("  3. Actualizar dosis")
        print("  4. Eliminar prescripción")
        print("  0. Volver al menú principal")
        opcion = input("Seleccione: ").strip()

        if opcion == "1":
            pid = leer_uuid("ID del paciente: ")
            medicamento = leer_texto("Medicamento: ")
            dosis = leer_texto("Dosis: ")
            crud.registrar_prescripcion(session, pid, medicamento, dosis)
            pausar()

        elif opcion == "2":
            pid = leer_uuid("ID del paciente: ")
            mostrar_prescripciones(session, pid)
            pausar()

        elif opcion == "3":
            pid = leer_uuid("ID del paciente: ")
            filas = mostrar_prescripciones(session, pid)
            if filas:
                try:
                    num = int(input("Número de prescripción a actualizar: ")) - 1
                    if 0 <= num < len(filas):
                        f = filas[num]
                        nueva = leer_texto("Nueva dosis: ")
                        crud.actualizar_dosis(session, f.paciente_id, f.fecha_prescripcion, f.prescripcion_id, nueva)
                    else:
                        print("✘ Número fuera de rango.")
                except ValueError:
                    print("✘ Ingrese un número válido.")
            pausar()

        elif opcion == "4":
            pid = leer_uuid("ID del paciente: ")
            filas = mostrar_prescripciones(session, pid)
            if filas:
                try:
                    num = int(input("Número de prescripción a eliminar: ")) - 1
                    if 0 <= num < len(filas):
                        f = filas[num]
                        crud.eliminar_prescripcion(session, f.paciente_id, f.fecha_prescripcion, f.prescripcion_id)
                    else:
                        print("✘ Número fuera de rango.")
                except ValueError:
                    print("✘ Ingrese un número válido.")
            pausar()

        elif opcion == "0":
            break
        else:
            print("✘ Opción inválida.")


# =============================================================
# Menú de procedimientos
# =============================================================

def mostrar_procedimientos(session, pid):
    """Muestra los procedimientos de un paciente y retorna la lista."""
    filas = crud.listar_procedimientos(session, pid)
    if not filas:
        print("  No hay procedimientos para este paciente.")
        return []
    print(f"\n  {'#':<3} {'Fecha':<25} {'Descripción'}")
    print("  " + "-" * 80)
    for i, f in enumerate(filas, 1):
        fecha_str = f.fecha_procedimiento.strftime("%Y-%m-%d %H:%M")
        print(f"  {i:<3} {fecha_str:<25} {f.descripcion or ''}")
    return filas


def menu_procedimientos(session):
    while True:
        print("\n--- Gestión de procedimientos ---")
        print("  1. Registrar procedimiento")
        print("  2. Ver procedimientos por paciente")
        print("  3. Actualizar descripción")
        print("  4. Eliminar procedimiento")
        print("  0. Volver al menú principal")
        opcion = input("Seleccione: ").strip()

        if opcion == "1":
            pid = leer_uuid("ID del paciente: ")
            descripcion = leer_texto("Descripción del procedimiento: ")
            crud.registrar_procedimiento(session, pid, descripcion)
            pausar()

        elif opcion == "2":
            pid = leer_uuid("ID del paciente: ")
            mostrar_procedimientos(session, pid)
            pausar()

        elif opcion == "3":
            pid = leer_uuid("ID del paciente: ")
            filas = mostrar_procedimientos(session, pid)
            if filas:
                try:
                    num = int(input("Número de procedimiento a actualizar: ")) - 1
                    if 0 <= num < len(filas):
                        f = filas[num]
                        nueva = leer_texto("Nueva descripción: ")
                        crud.actualizar_descripcion_procedimiento(
                            session, f.paciente_id, f.fecha_procedimiento, f.procedimiento_id, nueva)
                    else:
                        print("✘ Número fuera de rango.")
                except ValueError:
                    print("✘ Ingrese un número válido.")
            pausar()

        elif opcion == "4":
            pid = leer_uuid("ID del paciente: ")
            filas = mostrar_procedimientos(session, pid)
            if filas:
                try:
                    num = int(input("Número de procedimiento a eliminar: ")) - 1
                    if 0 <= num < len(filas):
                        f = filas[num]
                        crud.eliminar_procedimiento(
                            session, f.paciente_id, f.fecha_procedimiento, f.procedimiento_id)
                    else:
                        print("✘ Número fuera de rango.")
                except ValueError:
                    print("✘ Ingrese un número válido.")
            pausar()

        elif opcion == "0":
            break
        else:
            print("✘ Opción inválida.")


# =============================================================
# Menú principal
# =============================================================

def mostrar_menu():
    print("\n" + "=" * 45)
    print("  SISTEMA DE GESTIÓN DE PACIENTES CCSS")
    print("=" * 45)
    print("  1. Registrar paciente")
    print("  2. Consultar paciente")
    print("  3. Listar pacientes")
    print("  4. Actualizar paciente")
    print("  5. Eliminar paciente")
    print("  6. Gestionar consultas médicas")
    print("  7. Gestionar laboratorios")
    print("  8. Gestionar prescripciones")
    print("  9. Gestionar procedimientos")
    print(" 10. Cargar datos de prueba")
    print("  0. Salir")
    print("=" * 45)


def main():
    """Función principal: conecta con Cassandra e inicia el menú."""
    print("\n  Iniciando Sistema de Gestión de Pacientes CCSS...")
    cluster, session = database.conectar()

    # Si no se pudo conectar, terminar la aplicación
    if session is None:
        print("\n  La aplicación no puede iniciarse sin conexión a Cassandra.")
        print("  Verifique que Cassandra esté activo y que haya ejecutado schema.cql")
        return

    try:
        while True:
            mostrar_menu()
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                menu_registrar_paciente(session)
                pausar()
            elif opcion == "2":
                menu_consultar_paciente(session)
                pausar()
            elif opcion == "3":
                menu_listar_pacientes(session)
                pausar()
            elif opcion == "4":
                menu_actualizar_paciente(session)
                pausar()
            elif opcion == "5":
                menu_eliminar_paciente(session)
                pausar()
            elif opcion == "6":
                menu_consultas(session)
            elif opcion == "7":
                menu_laboratorios(session)
            elif opcion == "8":
                menu_prescripciones(session)
            elif opcion == "9":
                menu_procedimientos(session)
            elif opcion == "10":
                crud.insertar_datos_prueba(session)
                pausar()
            elif opcion == "0":
                print("\n  Cerrando el sistema...")
                break
            else:
                print("✘ Opción inválida. Ingrese un número del 0 al 10.")

    except KeyboardInterrupt:
        print("\n\n  Interrupción del usuario detectada.")

    finally:
        database.cerrar(cluster, session)


# Punto de entrada del script
if __name__ == "__main__":
    main()
