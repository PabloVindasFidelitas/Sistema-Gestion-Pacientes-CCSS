# Sistema de Gestión de Pacientes CCSS

Proyecto académico desarrollado para el curso de Bases de Datos NoSQL.

---

## Descripción del proyecto

El **Sistema de Gestión de Pacientes CCSS** es una aplicación de consola desarrollada en Python que simula la administración de información médica de pacientes de la Caja Costarricense de Seguro Social (CCSS) de Costa Rica.

El sistema permite registrar, consultar, actualizar y eliminar información sobre pacientes, así como gestionar sus consultas médicas, resultados de laboratorio, prescripciones y procedimientos.

Toda la información es almacenada en **Apache Cassandra**, una base de datos NoSQL orientada a columnas, diseñada para manejar grandes volúmenes de datos distribuidos.

> **Nota académica:** todos los datos utilizados en este proyecto son completamente ficticios y no representan personas ni información médica real.

---

## Tecnologías utilizadas

| Tecnología | Versión recomendada | Uso |
|---|---|---|
| Python | 3.11 o superior | Lenguaje principal de la aplicación |
| Apache Cassandra | 4.x o superior | Base de datos NoSQL |
| CQL (Cassandra Query Language) | — | Lenguaje de consulta para Cassandra |
| cassandra-driver | 3.29.2 | Librería oficial de Python para Cassandra |

---

## Estructura del proyecto

```text
Sistema-Gestion-Pacientes-CCSS/
│
├── main.py          → Menú interactivo de consola (punto de entrada)
├── database.py      → Configuración y conexión con Apache Cassandra
├── crud.py          → Operaciones CRUD para todas las tablas
├── schema.cql       → Instrucciones CQL para crear el keyspace y las tablas
├── requirements.txt → Dependencias de Python
├── README.md        → Documentación del proyecto
└── .gitignore       → Archivos excluidos del repositorio
```

### Descripción de cada archivo

- **`main.py`** — Contiene el menú principal y los submenús interactivos. Es el único archivo que el usuario necesita ejecutar.
- **`database.py`** — Define las funciones `conectar()` y `cerrar()` para gestionar la conexión con Cassandra.
- **`crud.py`** — Implementa todas las operaciones de creación, consulta, actualización y eliminación de registros usando consultas CQL parametrizadas.
- **`schema.cql`** — Define el keyspace `ccss_salud` y las cinco tablas del sistema. Debe ejecutarse una sola vez antes de iniciar la aplicación.
- **`requirements.txt`** — Lista la única dependencia necesaria: `cassandra-driver`.
- **`.gitignore`** — Excluye entornos virtuales, archivos compilados y archivos temporales del repositorio.

---

## Requisitos previos

Antes de instalar el proyecto, asegúrese de tener instalado:

- **Python 3.11 o superior** → https://www.python.org/downloads/
- **Apache Cassandra 4.x o superior** → https://cassandra.apache.org/download/
- **Java 11 o superior** (requerido por Cassandra) → https://adoptium.net/
- **cqlsh** (incluido con la instalación de Cassandra)
- **Git** → https://git-scm.com/

Para verificar las versiones instaladas:

```bash
python --version
java -version
cqlsh --version
```

---

## Instalación

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/PabloVindasFidelitas/Sistema-Gestion-Pacientes-CCSS.git
cd Sistema-Gestion-Pacientes-CCSS
```

### Paso 2 — Crear el entorno virtual de Python

```bash
python -m venv venv
```

### Paso 3 — Activar el entorno virtual

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

Una vez activado, el indicador del terminal mostrará `(venv)` al inicio de la línea.

### Paso 4 — Instalar las dependencias

```bash
pip install -r requirements.txt
```

### Paso 5 — Iniciar Apache Cassandra

**Linux / macOS (instalación local):**
```bash
cassandra -f
```

**Windows:**

Ejecute el script de inicio ubicado en la carpeta de instalación de Cassandra:
```cmd
C:\apache-cassandra\bin\cassandra.bat -f
```

Espere hasta que el log muestre el mensaje:
```
INFO  [main] ...Node localhost/127.0.0.1 state jump to NORMAL
```

### Paso 6 — Verificar que Cassandra esté escuchando en el puerto 9042

```bash
cqlsh
```

Si la conexión es exitosa, verá el prompt `cqlsh>`. Puede salir con `exit`.

### Paso 7 — Ejecutar el esquema CQL

Desde la raíz del proyecto, ejecute:

```bash
cqlsh -f schema.cql
```

Este comando crea el keyspace `ccss_salud` y las cinco tablas del sistema. Solo es necesario ejecutarlo una vez.

Para verificar que las tablas se crearon correctamente:

```bash
cqlsh -e "DESCRIBE TABLES;" ccss_salud
```

### Paso 8 — Iniciar la aplicación

```bash
python main.py
```

---

## Ejecución

Al iniciar la aplicación, verá el siguiente menú:

```
  Iniciando Sistema de Gestión de Pacientes CCSS...
✔ Conexión exitosa con Apache Cassandra en 127.0.0.1:9042
  Keyspace activo: ccss_salud

=============================================
  SISTEMA DE GESTIÓN DE PACIENTES CCSS
=============================================
  1. Registrar paciente
  2. Consultar paciente
  3. Listar pacientes
  4. Actualizar paciente
  5. Eliminar paciente
  6. Gestionar consultas médicas
  7. Gestionar laboratorios
  8. Gestionar prescripciones
  9. Gestionar procedimientos
 10. Cargar datos de prueba
  0. Salir
=============================================
Seleccione una opción:
```

### Ejemplo — Registrar un paciente

```
Seleccione una opción: 1

--- Registrar paciente ---
Nombre: Ana
Apellido: González
Fecha de nacimiento (YYYY-MM-DD): 1995-04-18
Teléfono: 8812-3456
✔ Paciente registrado con ID: f3a2b1c0-1234-5678-abcd-ef0123456789
```

### Ejemplo — Consultar un paciente

```
Seleccione una opción: 2

--- Consultar paciente ---
ID del paciente: f3a2b1c0-1234-5678-abcd-ef0123456789

  ID:               f3a2b1c0-1234-5678-abcd-ef0123456789
  Nombre:           Ana González
  Fecha nacimiento: 1995-04-18
  Teléfono:         8812-3456
```

### Ejemplo — Cargar datos de prueba

Seleccione la opción **10** para insertar automáticamente datos ficticios:

```
Seleccione una opción: 10

Insertando datos de prueba ficticios...
  ✔ 3 pacientes insertados.
  ✔ 2 consultas médicas insertadas.
  ✔ 2 resultados de laboratorio insertados.
  ✔ 2 prescripciones insertadas.
  ✔ 2 procedimientos insertados.

✔ Datos de prueba cargados correctamente.
  IDs de pacientes de prueba:
    Paciente 1 (Carlos Rodríguez): a0000000-0000-0000-0000-000000000001
    Paciente 2 (María Jiménez):    a0000000-0000-0000-0000-000000000002
    Paciente 3 (Luis Mora):         a0000000-0000-0000-0000-000000000003
```

---

## Funcionalidades

### Pacientes

| Operación | Descripción |
|---|---|
| Registrar | Crea un nuevo paciente con nombre, apellido, fecha de nacimiento y teléfono |
| Consultar | Recupera los datos de un paciente por su UUID |
| Listar | Muestra todos los pacientes registrados |
| Actualizar | Modifica el número de teléfono de un paciente |
| Eliminar | Elimina el paciente y todos sus registros médicos asociados |

### Consultas médicas

| Operación | Descripción |
|---|---|
| Registrar | Crea una consulta con diagnóstico y observaciones |
| Historial | Muestra las consultas de un paciente, de más reciente a más antigua |
| Actualizar | Modifica el diagnóstico de una consulta específica |
| Eliminar | Elimina una consulta específica |

### Laboratorios

| Operación | Descripción |
|---|---|
| Registrar | Guarda un resultado de laboratorio con tipo de examen y resultado |
| Consultar | Lista todos los resultados de un paciente |
| Actualizar | Modifica el resultado de un examen |
| Eliminar | Elimina un resultado específico |

### Prescripciones

| Operación | Descripción |
|---|---|
| Registrar | Crea una prescripción con medicamento y dosis |
| Consultar | Lista todas las prescripciones de un paciente |
| Actualizar | Modifica la dosis de una prescripción |
| Eliminar | Elimina una prescripción específica |

### Procedimientos

| Operación | Descripción |
|---|---|
| Registrar | Crea un procedimiento médico con su descripción |
| Consultar | Lista todos los procedimientos de un paciente |
| Actualizar | Modifica la descripción de un procedimiento |
| Eliminar | Elimina un procedimiento específico |

---

## Ejemplos de consultas CQL

Las siguientes consultas pueden ejecutarse directamente desde `cqlsh` para verificar los datos almacenados.

### Seleccionar el keyspace

```cql
USE ccss_salud;
```

### INSERT — Insertar un paciente

```cql
INSERT INTO pacientes (paciente_id, nombre, apellido, fecha_nacimiento, telefono)
VALUES (uuid(), 'Juan', 'Pérez', '1988-03-15', '8899-1234');
```

### SELECT — Listar todos los pacientes

```cql
SELECT * FROM pacientes;
```

### SELECT — Consultar historial de consultas de un paciente

```cql
SELECT * FROM consultas_por_paciente
WHERE paciente_id = a0000000-0000-0000-0000-000000000001;
```

### UPDATE — Actualizar el teléfono de un paciente

```cql
UPDATE pacientes
SET telefono = '8811-9999'
WHERE paciente_id = a0000000-0000-0000-0000-000000000001;
```

### UPDATE — Actualizar el diagnóstico de una consulta

```cql
UPDATE consultas_por_paciente
SET diagnostico = 'Hipertensión arterial moderada'
WHERE paciente_id = a0000000-0000-0000-0000-000000000001
  AND fecha_consulta = '2024-06-10 09:00:00+0000'
  AND consulta_id = b0000000-0000-0000-0000-000000000001;
```

### DELETE — Eliminar un resultado de laboratorio

```cql
DELETE FROM laboratorios_por_paciente
WHERE paciente_id = a0000000-0000-0000-0000-000000000001
  AND fecha_resultado = '2024-06-11 08:00:00+0000'
  AND laboratorio_id = c0000000-0000-0000-0000-000000000001;
```

### DELETE — Eliminar un paciente completo

```cql
DELETE FROM pacientes WHERE paciente_id = a0000000-0000-0000-0000-000000000001;
```

> **Nota:** Al eliminar un paciente desde la aplicación (opción 5), se eliminan automáticamente todos sus registros médicos. Desde `cqlsh`, debe hacerlo manualmente en cada tabla si lo desea.

---

## Pruebas

### Prueba manual recomendada

1. Ejecute `python main.py`.
2. Seleccione la opción **10** para cargar los datos de prueba.
3. Seleccione la opción **3** (Listar pacientes) para verificar que los tres pacientes ficticios aparecen.
4. Copie el ID de un paciente (por ejemplo, `a0000000-0000-0000-0000-000000000001`).
5. Seleccione la opción **6** (Gestionar consultas médicas) → **2** (Ver historial).
6. Pegue el ID del paciente y verifique que las consultas aparecen ordenadas de más reciente a más antigua.
7. Pruebe actualizar y eliminar un registro para confirmar que las operaciones funcionan.

### Verificación directa en cqlsh

```bash
cqlsh
```

```cql
USE ccss_salud;
SELECT * FROM pacientes;
SELECT * FROM consultas_por_paciente WHERE paciente_id = a0000000-0000-0000-0000-000000000001;
SELECT * FROM laboratorios_por_paciente WHERE paciente_id = a0000000-0000-0000-0000-000000000001;
SELECT * FROM prescripciones_por_paciente WHERE paciente_id = a0000000-0000-0000-0000-000000000002;
SELECT * FROM procedimientos_por_paciente WHERE paciente_id = a0000000-0000-0000-0000-000000000003;
```

---

## Problemas comunes

### Cassandra no está ejecutándose

**Síntoma:**
```
✘ Error al conectar con Cassandra: ...
```

**Solución:**

Asegúrese de que el servicio de Cassandra esté activo antes de iniciar la aplicación:

```bash
# Linux / macOS
cassandra -f

# Windows
C:\apache-cassandra\bin\cassandra.bat -f
```

---

### Error de conexión al puerto 9042

**Síntoma:**
```
✘ Error: La conexión con Cassandra agotó el tiempo de espera.
```

**Solución:**

Verifique que Cassandra esté escuchando en el puerto correcto:

```bash
# Linux / macOS
netstat -an | grep 9042

# Windows PowerShell
netstat -ano | Select-String "9042"
```

Si el puerto está bloqueado por un firewall, permita el tráfico en el puerto 9042.

---

### El keyspace `ccss_salud` no existe

**Síntoma:**
```
✘ Error al conectar con Cassandra: Keyspace 'ccss_salud' does not exist
```

**Solución:**

Ejecute el esquema CQL:

```bash
cqlsh -f schema.cql
```

---

### La librería `cassandra-driver` no está instalada

**Síntoma:**
```
ModuleNotFoundError: No module named 'cassandra'
```

**Solución:**

Active el entorno virtual e instale las dependencias:

```bash
# Windows
venv\Scripts\Activate.ps1

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

---

### UUID inválido

**Síntoma:**
```
✘ UUID inválido. Use el formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Solución:**

Copie el UUID directamente desde la salida de la aplicación o de `cqlsh`. Un UUID válido tiene el formato:

```
a0000000-0000-0000-0000-000000000001
```

---

## Repositorio

https://github.com/PabloVindasFidelitas/Sistema-Gestion-Pacientes-CCSS

---

## Autor

Proyecto académico — Bases de Datos NoSQL  
Caja Costarricense de Seguro Social (CCSS) — Simulación académica
