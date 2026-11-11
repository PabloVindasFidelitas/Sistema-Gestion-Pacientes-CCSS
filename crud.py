# =============================================================
# crud.py
# Operaciones CRUD para todas las tablas del sistema CCSS
# Utiliza consultas CQL parametrizadas y prepared statements
# =============================================================

import uuid
from datetime import datetime


# =============================================================
# SECCIÓN: PACIENTES
# =============================================================

def crear_paciente(session, nombre, apellido, fecha_nacimiento, telefono):
    """
    Registra un nuevo paciente en la tabla 'pacientes'.

    Parámetros:
        session: sesión activa de Cassandra.
        nombre (str): nombre del paciente.
        apellido (str): apellido del paciente.
        fecha_nacimiento (date): fecha de nacimiento.
        telefono (str): número de teléfono.

    Retorna:
        UUID del paciente creado.
    """
    paciente_id = uuid.uuid4()
    query = session.prepare("""
        INSERT INTO pacientes (paciente_id, nombre, apellido, fecha_nacimiento, telefono)
        VALUES (?, ?, ?, ?, ?)
    """)
    session.execute(query, (paciente_id, nombre, apellido, fecha_nacimiento, telefono))
    print(f"✔ Paciente registrado con ID: {paciente_id}")
    return paciente_id


def obtener_paciente(session, paciente_id):
    """
    Consulta un paciente por su UUID.

    Retorna:
        Fila con los datos del paciente o None si no existe.
    """
    query = session.prepare("SELECT * FROM pacientes WHERE paciente_id = ?")
    resultado = session.execute(query, (paciente_id,))
    fila = resultado.one()
    return fila


def listar_pacientes(session):
    """
    Lista todos los pacientes registrados en el sistema.
    Nota: SELECT sin WHERE funciona en Cassandra para tablas pequeñas
    en un entorno académico local.

    Retorna:
        Lista de filas con todos los pacientes.
    """
    resultado = session.execute("SELECT * FROM pacientes")
    return list(resultado)


def actualizar_telefono_paciente(session, paciente_id, nuevo_telefono):
    """
    Actualiza el teléfono de un paciente existente.
    Verifica que el paciente exista antes de actualizar para
    evitar crear un registro vacío (comportamiento upsert de Cassandra).

    Retorna:
        True si se actualizó, False si el paciente no existe.
    """
    # Verificar que el paciente exista antes de actualizar
    if not obtener_paciente(session, paciente_id):
        print("✘ El paciente no existe.")
        return False

    query = session.prepare("""
        UPDATE pacientes SET telefono = ?
        WHERE paciente_id = ?
    """)
    session.execute(query, (nuevo_telefono, paciente_id))
    print("✔ Teléfono actualizado correctamente.")
    return True


def eliminar_paciente(session, paciente_id):
    """
    Elimina un paciente y todos sus registros médicos asociados.
    Se eliminan primero los registros de las tablas dependientes
    para evitar datos huérfanos.

    Retorna:
        True si se eliminó, False si el paciente no existe.
    """
    if not obtener_paciente(session, paciente_id):
        print("✘ El paciente no existe.")
        return False

    # Eliminar registros médicos asociados al paciente
    tablas_medicas = [
        "consultas_por_paciente",
        "laboratorios_por_paciente",
        "prescripciones_por_paciente",
        "procedimientos_por_paciente"
    ]
    for tabla in tablas_medicas:
        query = session.prepare(f"DELETE FROM {tabla} WHERE paciente_id = ?")
        session.execute(query, (paciente_id,))

    # Eliminar el paciente
    query = session.prepare("DELETE FROM pacientes WHERE paciente_id = ?")
    session.execute(query, (paciente_id,))
    print("✔ Paciente y todos sus registros médicos eliminados correctamente.")
    return True


# =============================================================
# SECCIÓN: CONSULTAS MÉDICAS
# =============================================================

def registrar_consulta(session, paciente_id, diagnostico, observaciones):
    """
    Registra una nueva consulta médica para un paciente.
    La fecha se asigna automáticamente al momento del registro.

    Retorna:
        Tuple (consulta_id, fecha_consulta) del registro creado.
    """
    consulta_id = uuid.uuid4()
    fecha_consulta = datetime.utcnow()
    query = session.prepare("""
        INSERT INTO consultas_por_paciente
            (paciente_id, fecha_consulta, consulta_id, diagnostico, observaciones)
        VALUES (?, ?, ?, ?, ?)
    """)
    session.execute(query, (paciente_id, fecha_consulta, consulta_id, diagnostico, observaciones))
    print(f"✔ Consulta registrada con ID: {consulta_id}")
    return consulta_id, fecha_consulta


def listar_consultas(session, paciente_id):
    """
    Retorna el historial de consultas de un paciente, ordenadas
    de más reciente a más antigua (definido en el esquema).

    Retorna:
        Lista de filas de consultas.
    """
    query = session.prepare("""
        SELECT * FROM consultas_por_paciente WHERE paciente_id = ?
    """)
    resultado = session.execute(query, (paciente_id,))
    return list(resultado)


def actualizar_diagnostico(session, paciente_id, fecha_consulta, consulta_id, nuevo_diagnostico):
    """
    Actualiza el diagnóstico de una consulta específica.
    Requiere la clave primaria completa para evitar crear un registro nuevo.

    Retorna:
        True si se actualizó correctamente.
    """
    # Verificar que la consulta exista
    query_buscar = session.prepare("""
        SELECT consulta_id FROM consultas_por_paciente
        WHERE paciente_id = ? AND fecha_consulta = ? AND consulta_id = ?
    """)
    if not session.execute(query_buscar, (paciente_id, fecha_consulta, consulta_id)).one():
        print("✘ La consulta no existe.")
        return False

    query = session.prepare("""
        UPDATE consultas_por_paciente SET diagnostico = ?
        WHERE paciente_id = ? AND fecha_consulta = ? AND consulta_id = ?
    """)
    session.execute(query, (nuevo_diagnostico, paciente_id, fecha_consulta, consulta_id))
    print("✔ Diagnóstico actualizado correctamente.")
    return True


def eliminar_consulta(session, paciente_id, fecha_consulta, consulta_id):
    """
    Elimina una consulta médica específica.
    Requiere la clave primaria completa.
    """
    query = session.prepare("""
        DELETE FROM consultas_por_paciente
        WHERE paciente_id = ? AND fecha_consulta = ? AND consulta_id = ?
    """)
    session.execute(query, (paciente_id, fecha_consulta, consulta_id))
    print("✔ Consulta eliminada correctamente.")


# =============================================================
# SECCIÓN: LABORATORIOS
# =============================================================

def registrar_laboratorio(session, paciente_id, tipo_examen, resultado):
    """
    Registra un nuevo resultado de laboratorio para un paciente.

    Retorna:
        Tuple (laboratorio_id, fecha_resultado) del registro creado.
    """
    laboratorio_id = uuid.uuid4()
    fecha_resultado = datetime.utcnow()
    query = session.prepare("""
        INSERT INTO laboratorios_por_paciente
            (paciente_id, fecha_resultado, laboratorio_id, tipo_examen, resultado)
        VALUES (?, ?, ?, ?, ?)
    """)
    session.execute(query, (paciente_id, fecha_resultado, laboratorio_id, tipo_examen, resultado))
    print(f"✔ Resultado de laboratorio registrado con ID: {laboratorio_id}")
    return laboratorio_id, fecha_resultado


def listar_laboratorios(session, paciente_id):
    """
    Retorna todos los resultados de laboratorio de un paciente.

    Retorna:
        Lista de filas de laboratorios.
    """
    query = session.prepare("""
        SELECT * FROM laboratorios_por_paciente WHERE paciente_id = ?
    """)
    resultado = session.execute(query, (paciente_id,))
    return list(resultado)


def actualizar_resultado_laboratorio(session, paciente_id, fecha_resultado, laboratorio_id, nuevo_resultado):
    """
    Actualiza el resultado de un examen de laboratorio específico.
    Verifica la existencia del registro antes de actualizar.
    """
    query_buscar = session.prepare("""
        SELECT laboratorio_id FROM laboratorios_por_paciente
        WHERE paciente_id = ? AND fecha_resultado = ? AND laboratorio_id = ?
    """)
    if not session.execute(query_buscar, (paciente_id, fecha_resultado, laboratorio_id)).one():
        print("✘ El resultado de laboratorio no existe.")
        return False

    query = session.prepare("""
        UPDATE laboratorios_por_paciente SET resultado = ?
        WHERE paciente_id = ? AND fecha_resultado = ? AND laboratorio_id = ?
    """)
    session.execute(query, (nuevo_resultado, paciente_id, fecha_resultado, laboratorio_id))
    print("✔ Resultado actualizado correctamente.")
    return True


def eliminar_laboratorio(session, paciente_id, fecha_resultado, laboratorio_id):
    """
    Elimina un resultado de laboratorio específico.
    """
    query = session.prepare("""
        DELETE FROM laboratorios_por_paciente
        WHERE paciente_id = ? AND fecha_resultado = ? AND laboratorio_id = ?
    """)
    session.execute(query, (paciente_id, fecha_resultado, laboratorio_id))
    print("✔ Resultado de laboratorio eliminado correctamente.")


# =============================================================
# SECCIÓN: PRESCRIPCIONES
# =============================================================

def registrar_prescripcion(session, paciente_id, medicamento, dosis):
    """
    Registra una nueva prescripción médica para un paciente.

    Retorna:
        Tuple (prescripcion_id, fecha_prescripcion) del registro creado.
    """
    prescripcion_id = uuid.uuid4()
    fecha_prescripcion = datetime.utcnow()
    query = session.prepare("""
        INSERT INTO prescripciones_por_paciente
            (paciente_id, fecha_prescripcion, prescripcion_id, medicamento, dosis)
        VALUES (?, ?, ?, ?, ?)
    """)
    session.execute(query, (paciente_id, fecha_prescripcion, prescripcion_id, medicamento, dosis))
    print(f"✔ Prescripción registrada con ID: {prescripcion_id}")
    return prescripcion_id, fecha_prescripcion


def listar_prescripciones(session, paciente_id):
    """
    Retorna todas las prescripciones de un paciente.

    Retorna:
        Lista de filas de prescripciones.
    """
    query = session.prepare("""
        SELECT * FROM prescripciones_por_paciente WHERE paciente_id = ?
    """)
    resultado = session.execute(query, (paciente_id,))
    return list(resultado)


def actualizar_dosis(session, paciente_id, fecha_prescripcion, prescripcion_id, nueva_dosis):
    """
    Actualiza la dosis de una prescripción específica.
    Verifica la existencia del registro antes de actualizar.
    """
    query_buscar = session.prepare("""
        SELECT prescripcion_id FROM prescripciones_por_paciente
        WHERE paciente_id = ? AND fecha_prescripcion = ? AND prescripcion_id = ?
    """)
    if not session.execute(query_buscar, (paciente_id, fecha_prescripcion, prescripcion_id)).one():
        print("✘ La prescripción no existe.")
        return False

    query = session.prepare("""
        UPDATE prescripciones_por_paciente SET dosis = ?
        WHERE paciente_id = ? AND fecha_prescripcion = ? AND prescripcion_id = ?
    """)
    session.execute(query, (nueva_dosis, paciente_id, fecha_prescripcion, prescripcion_id))
    print("✔ Dosis actualizada correctamente.")
    return True


def eliminar_prescripcion(session, paciente_id, fecha_prescripcion, prescripcion_id):
    """
    Elimina una prescripción médica específica.
    """
    query = session.prepare("""
        DELETE FROM prescripciones_por_paciente
        WHERE paciente_id = ? AND fecha_prescripcion = ? AND prescripcion_id = ?
    """)
    session.execute(query, (paciente_id, fecha_prescripcion, prescripcion_id))
    print("✔ Prescripción eliminada correctamente.")


# =============================================================
# SECCIÓN: PROCEDIMIENTOS
# =============================================================

def registrar_procedimiento(session, paciente_id, descripcion):
    """
    Registra un nuevo procedimiento médico para un paciente.

    Retorna:
        Tuple (procedimiento_id, fecha_procedimiento) del registro creado.
    """
    procedimiento_id = uuid.uuid4()
    fecha_procedimiento = datetime.utcnow()
    query = session.prepare("""
        INSERT INTO procedimientos_por_paciente
            (paciente_id, fecha_procedimiento, procedimiento_id, descripcion)
        VALUES (?, ?, ?, ?)
    """)
    session.execute(query, (paciente_id, fecha_procedimiento, procedimiento_id, descripcion))
    print(f"✔ Procedimiento registrado con ID: {procedimiento_id}")
    return procedimiento_id, fecha_procedimiento


def listar_procedimientos(session, paciente_id):
    """
    Retorna todos los procedimientos médicos de un paciente.

    Retorna:
        Lista de filas de procedimientos.
    """
    query = session.prepare("""
        SELECT * FROM procedimientos_por_paciente WHERE paciente_id = ?
    """)
    resultado = session.execute(query, (paciente_id,))
    return list(resultado)


def actualizar_descripcion_procedimiento(session, paciente_id, fecha_procedimiento, procedimiento_id, nueva_descripcion):
    """
    Actualiza la descripción de un procedimiento específico.
    Verifica la existencia del registro antes de actualizar.
    """
    query_buscar = session.prepare("""
        SELECT procedimiento_id FROM procedimientos_por_paciente
        WHERE paciente_id = ? AND fecha_procedimiento = ? AND procedimiento_id = ?
    """)
    if not session.execute(query_buscar, (paciente_id, fecha_procedimiento, procedimiento_id)).one():
        print("✘ El procedimiento no existe.")
        return False

    query = session.prepare("""
        UPDATE procedimientos_por_paciente SET descripcion = ?
        WHERE paciente_id = ? AND fecha_procedimiento = ? AND procedimiento_id = ?
    """)
    session.execute(query, (nueva_descripcion, paciente_id, fecha_procedimiento, procedimiento_id))
    print("✔ Descripción actualizada correctamente.")
    return True


def eliminar_procedimiento(session, paciente_id, fecha_procedimiento, procedimiento_id):
    """
    Elimina un procedimiento médico específico.
    """
    query = session.prepare("""
        DELETE FROM procedimientos_por_paciente
        WHERE paciente_id = ? AND fecha_procedimiento = ? AND procedimiento_id = ?
    """)
    session.execute(query, (paciente_id, fecha_procedimiento, procedimiento_id))
    print("✔ Procedimiento eliminado correctamente.")


# =============================================================
# SECCIÓN: DATOS DE PRUEBA
# =============================================================

def insertar_datos_prueba(session):
    """
    Inserta datos ficticios de demostración en todas las tablas.
    Utiliza IDs fijos para evitar duplicados al ejecutarse múltiples veces.
    Los datos son completamente ficticios y no representan personas reales.
    """
    from datetime import date

    print("\nInsertando datos de prueba ficticios...")

    # UUIDs fijos para los pacientes de prueba (evita duplicados)
    id_p1 = uuid.UUID("a0000000-0000-0000-0000-000000000001")
    id_p2 = uuid.UUID("a0000000-0000-0000-0000-000000000002")
    id_p3 = uuid.UUID("a0000000-0000-0000-0000-000000000003")

    # --- Pacientes ficticios ---
    pacientes = [
        (id_p1, "Carlos", "Rodríguez", date(1985, 3, 14), "8800-1111"),
        (id_p2, "María",  "Jiménez",   date(1990, 7, 22), "8800-2222"),
        (id_p3, "Luis",   "Mora",       date(1978, 11, 5), "8800-3333"),
    ]
    query_p = session.prepare("""
        INSERT INTO pacientes (paciente_id, nombre, apellido, fecha_nacimiento, telefono)
        VALUES (?, ?, ?, ?, ?)
    """)
    for p in pacientes:
        session.execute(query_p, p)
    print(f"  ✔ {len(pacientes)} pacientes insertados.")

    # UUIDs fijos para registros médicos de prueba
    id_c1 = uuid.UUID("b0000000-0000-0000-0000-000000000001")
    id_c2 = uuid.UUID("b0000000-0000-0000-0000-000000000002")
    fecha_c1 = datetime(2024, 6, 10, 9, 0, 0)
    fecha_c2 = datetime(2024, 8, 15, 14, 30, 0)

    # --- Consultas médicas ficticias ---
    query_c = session.prepare("""
        INSERT INTO consultas_por_paciente
            (paciente_id, fecha_consulta, consulta_id, diagnostico, observaciones)
        VALUES (?, ?, ?, ?, ?)
    """)
    session.execute(query_c, (id_p1, fecha_c1, id_c1,
                              "Hipertensión arterial leve",
                              "Se recomienda reducir consumo de sal y hacer ejercicio."))
    session.execute(query_c, (id_p2, fecha_c2, id_c2,
                              "Gripe estacional",
                              "Reposo por 3 días. Control en una semana."))
    print("  ✔ 2 consultas médicas insertadas.")

    # --- Resultados de laboratorio ficticios ---
    id_l1 = uuid.UUID("c0000000-0000-0000-0000-000000000001")
    id_l2 = uuid.UUID("c0000000-0000-0000-0000-000000000002")
    fecha_l1 = datetime(2024, 6, 11, 8, 0, 0)
    fecha_l2 = datetime(2024, 8, 16, 10, 0, 0)

    query_l = session.prepare("""
        INSERT INTO laboratorios_por_paciente
            (paciente_id, fecha_resultado, laboratorio_id, tipo_examen, resultado)
        VALUES (?, ?, ?, ?, ?)
    """)
    session.execute(query_l, (id_p1, fecha_l1, id_l1,
                              "Hemograma completo",
                              "Glóbulos rojos: 4.8 M/uL. Sin anomalías detectadas."))
    session.execute(query_l, (id_p2, fecha_l2, id_l2,
                              "Glucosa en ayunas",
                              "95 mg/dL. Dentro del rango normal."))
    print("  ✔ 2 resultados de laboratorio insertados.")

    # --- Prescripciones ficticias ---
    id_rx1 = uuid.UUID("d0000000-0000-0000-0000-000000000001")
    id_rx2 = uuid.UUID("d0000000-0000-0000-0000-000000000002")
    fecha_rx1 = datetime(2024, 6, 10, 9, 30, 0)
    fecha_rx2 = datetime(2024, 8, 15, 15, 0, 0)

    query_rx = session.prepare("""
        INSERT INTO prescripciones_por_paciente
            (paciente_id, fecha_prescripcion, prescripcion_id, medicamento, dosis)
        VALUES (?, ?, ?, ?, ?)
    """)
    session.execute(query_rx, (id_p1, fecha_rx1, id_rx1,
                               "Enalapril",
                               "10 mg cada 12 horas por 30 días."))
    session.execute(query_rx, (id_p2, fecha_rx2, id_rx2,
                               "Paracetamol",
                               "500 mg cada 8 horas por 5 días."))
    print("  ✔ 2 prescripciones insertadas.")

    # --- Procedimientos ficticios ---
    id_pr1 = uuid.UUID("e0000000-0000-0000-0000-000000000001")
    id_pr2 = uuid.UUID("e0000000-0000-0000-0000-000000000002")
    fecha_pr1 = datetime(2024, 7, 5, 7, 0, 0)
    fecha_pr2 = datetime(2024, 9, 20, 8, 0, 0)

    query_pr = session.prepare("""
        INSERT INTO procedimientos_por_paciente
            (paciente_id, fecha_procedimiento, procedimiento_id, descripcion)
        VALUES (?, ?, ?, ?)
    """)
    session.execute(query_pr, (id_p3, fecha_pr1, id_pr1,
                               "Electrocardiograma de rutina. Sin hallazgos anormales."))
    session.execute(query_pr, (id_p3, fecha_pr2, id_pr2,
                               "Extracción de molar inferior derecho bajo anestesia local."))
    print("  ✔ 2 procedimientos insertados.")

    print("\n✔ Datos de prueba cargados correctamente.")
    print(f"  IDs de pacientes de prueba:")
    print(f"    Paciente 1 (Carlos Rodríguez): {id_p1}")
    print(f"    Paciente 2 (María Jiménez):    {id_p2}")
    print(f"    Paciente 3 (Luis Mora):         {id_p3}")
