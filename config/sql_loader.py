import os

from sqlalchemy import text

from config import db


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_DIR = os.path.join(BASE_DIR, "sql")


def cargar_archivo_sql(file_path: str, obligatorio: bool = True) -> bool:
    """Ejecuta un archivo SQL sobre la conexión principal de la API."""
    if not os.path.exists(file_path):
        mensaje = f"El archivo SQL no existe: {file_path}"
        if obligatorio:
            raise FileNotFoundError(mensaje)
        print(f"Aviso: {mensaje}")
        return False

    with open(file_path, "r", encoding="utf-8") as file:
        sql_script = file.read().strip()

    if not sql_script:
        print(f"Aviso: archivo SQL vacío: {file_path}")
        return False

    statements = [s.strip() for s in sql_script.split(";") if s.strip()]

    with db.engine.connect() as conn:
        for statement in statements:
            conn.execute(text(statement))
        conn.commit()

    print(f"SQL ejecutado: {file_path}")
    return True


def tabla_tiene_registros(tabla: str) -> bool:
    with db.engine.connect() as conn:
        resultado = conn.execute(text(f"SELECT COUNT(*) AS total FROM {tabla}"))
        fila = resultado.fetchone()
        total = int(fila[0]) if fila else 0
        return total > 0


def cargar_datos_iniciales() -> None:
    """Carga los inserts iniciales. Se omite si la tabla usuarios ya tiene datos."""
    if tabla_tiene_registros("usuarios"):
        print("Carga inicial omitida: la tabla usuarios ya tiene datos.")
        return

    archivos = [
        os.path.join(SQL_DIR, "insert_productos.sql"),
        os.path.join(SQL_DIR, "insert_sectores.sql"),
        os.path.join(SQL_DIR, "insert_operarios.sql"),
        os.path.join(SQL_DIR, "insert_roles.sql"),
        os.path.join(SQL_DIR, "insert_labores.sql"),
    ]

    for ruta in archivos:
        cargar_archivo_sql(ruta, obligatorio=True)
