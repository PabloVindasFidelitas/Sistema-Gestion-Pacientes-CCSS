-- =============================================================
-- Sistema de Gestión de Pacientes CCSS
-- Esquema de base de datos Apache Cassandra
-- Ejecutar con: cqlsh -f schema.cql
-- =============================================================

-- Crear el keyspace para el sistema
-- SimpleStrategy se utiliza exclusivamente para entornos académicos locales
CREATE KEYSPACE IF NOT EXISTS ccss_salud
    WITH REPLICATION = {
        'class': 'SimpleStrategy',
        'replication_factor': 1
    };

-- Seleccionar el keyspace
USE ccss_salud;

-- =============================================================
-- Tabla: pacientes
-- Almacena la información básica de cada paciente.
-- Clave primaria simple: paciente_id (UUID único por paciente)
-- =============================================================
CREATE TABLE IF NOT EXISTS pacientes (
    paciente_id  UUID,
    nombre       TEXT,
    apellido     TEXT,
    fecha_nacimiento DATE,
    telefono     TEXT,
    PRIMARY KEY (paciente_id)
);

-- =============================================================
-- Tabla: consultas_por_paciente
-- Almacena el historial de consultas médicas de cada paciente.
-- Clave primaria compuesta: paciente_id + fecha_consulta + consulta_id
-- El orden descendente muestra primero las consultas más recientes.
-- =============================================================
CREATE TABLE IF NOT EXISTS consultas_por_paciente (
    paciente_id     UUID,
    fecha_consulta  TIMESTAMP,
    consulta_id     UUID,
    diagnostico     TEXT,
    observaciones   TEXT,
    PRIMARY KEY ((paciente_id), fecha_consulta, consulta_id)
) WITH CLUSTERING ORDER BY (fecha_consulta DESC, consulta_id ASC);

-- =============================================================
-- Tabla: laboratorios_por_paciente
-- Almacena los resultados de exámenes de laboratorio por paciente.
-- Clave primaria compuesta: paciente_id + fecha_resultado + laboratorio_id
-- =============================================================
CREATE TABLE IF NOT EXISTS laboratorios_por_paciente (
    paciente_id      UUID,
    fecha_resultado  TIMESTAMP,
    laboratorio_id   UUID,
    tipo_examen      TEXT,
    resultado        TEXT,
    PRIMARY KEY ((paciente_id), fecha_resultado, laboratorio_id)
) WITH CLUSTERING ORDER BY (fecha_resultado DESC, laboratorio_id ASC);

-- =============================================================
-- Tabla: prescripciones_por_paciente
-- Almacena las prescripciones médicas asignadas a cada paciente.
-- Clave primaria compuesta: paciente_id + fecha_prescripcion + prescripcion_id
-- =============================================================
CREATE TABLE IF NOT EXISTS prescripciones_por_paciente (
    paciente_id        UUID,
    fecha_prescripcion TIMESTAMP,
    prescripcion_id    UUID,
    medicamento        TEXT,
    dosis              TEXT,
    PRIMARY KEY ((paciente_id), fecha_prescripcion, prescripcion_id)
) WITH CLUSTERING ORDER BY (fecha_prescripcion DESC, prescripcion_id ASC);

-- =============================================================
-- Tabla: procedimientos_por_paciente
-- Almacena los procedimientos médicos realizados a cada paciente.
-- Clave primaria compuesta: paciente_id + fecha_procedimiento + procedimiento_id
-- =============================================================
CREATE TABLE IF NOT EXISTS procedimientos_por_paciente (
    paciente_id          UUID,
    fecha_procedimiento  TIMESTAMP,
    procedimiento_id     UUID,
    descripcion          TEXT,
    PRIMARY KEY ((paciente_id), fecha_procedimiento, procedimiento_id)
) WITH CLUSTERING ORDER BY (fecha_procedimiento DESC, procedimiento_id ASC);
