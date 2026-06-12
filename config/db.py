from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os
import time
from sqlalchemy.exc import OperationalError

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = quote_plus(os.getenv("DB_PASSWORD", ""))
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "3306")
db_name = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

print(f"Usuario: {db_user}, Host: {db_host}, Puerto: {db_port}, DB: {db_name}")


def try_connect(db_url):
    """Intenta conectar a la base de datos con reintentos."""
    print(f"Conectando a: {db_url}")
    attempt = 1
    max_attempts = 5

    while attempt <= max_attempts:
        try:
            test_engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=3600)
            with test_engine.connect() as connection:
                print(f"✓ Conectado a la base de datos en {db_url}")
                return test_engine
        except OperationalError as e:
            if "1049" in str(e):
                print("La base de datos no existe. Continuando con la creación...")
                return None
            print(f"Intento {attempt}/{max_attempts} - Error al conectar: {e}")
            if attempt < max_attempts:
                print("Reintentando en 3 segundos...")
                time.sleep(3)
            attempt += 1

    return None


Base = declarative_base()

engine = try_connect(DATABASE_URL)


def initialize_engine():
    global engine, SessionLocal
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


if engine is None:
    print("Inicializando el motor después de la creación de la base de datos...")
    initialize_engine()

if engine is None:
    print("La base de datos será creada por la lógica en main.py.")
else:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
