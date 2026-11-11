# =============================================================
# database.py
# Configuración y conexión con Apache Cassandra
# =============================================================

from cassandra.cluster import Cluster
from cassandra import OperationTimedOut
from cassandra.policies import RoundRobinPolicy

# Parámetros de conexión (entorno local académico)
CASSANDRA_HOST = '127.0.0.1'
CASSANDRA_PORT = 9042
KEYSPACE = 'ccss_salud'


def conectar():
    """
    Establece la conexión con el clúster de Apache Cassandra
    y retorna la sesión activa del keyspace ccss_salud.

    Retorna:
        tuple: (cluster, session) si la conexión fue exitosa.
        (None, None) si ocurrió algún error.
    """
    try:
        cluster = Cluster(
            [CASSANDRA_HOST],
            port=CASSANDRA_PORT,
            load_balancing_policy=RoundRobinPolicy(),
            connect_timeout=10
        )
        session = cluster.connect(KEYSPACE)
        print(f"✔ Conexión exitosa con Apache Cassandra en {CASSANDRA_HOST}:{CASSANDRA_PORT}")
        print(f"  Keyspace activo: {KEYSPACE}\n")
        return cluster, session

    except OperationTimedOut:
        print("✘ Error: La conexión con Cassandra agotó el tiempo de espera.")
        print("  Verifique que Apache Cassandra esté ejecutándose en el puerto 9042.")
        return None, None

    except Exception as e:
        print(f"✘ Error al conectar con Cassandra: {e}")
        print("  Asegúrese de que Cassandra esté activo y el keyspace 'ccss_salud' exista.")
        print("  Ejecute primero: cqlsh -f schema.cql")
        return None, None


def cerrar(cluster, session):
    """
    Cierra correctamente la sesión y el clúster de Cassandra.

    Parámetros:
        cluster: instancia del Cluster de Cassandra.
        session: sesión activa de Cassandra.
    """
    try:
        if session:
            session.shutdown()
        if cluster:
            cluster.shutdown()
        print("\n✔ Conexión cerrada correctamente.")
    except Exception as e:
        print(f"✘ Error al cerrar la conexión: {e}")
