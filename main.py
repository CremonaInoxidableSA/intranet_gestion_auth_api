from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import create_engine, text 
from config import db
from config.sql_loader import cargar_datos_iniciales

from routes.get.usuarios import router as usuarios_router
from routes.get.data_usuarios import router as data_usuarios_router
from routes.get.recuperacion_check import router as recuperacion_check_router

from routes.get.roles import router as roles_router

from routes.set.deshabilitar_usuario import router as deshabilitar_usuario_router
from routes.set.habilitar_usuario import router as habilitar_usuario_router

from routes.gestion_usuarios.crear_o_editar_usuario import router as crear_o_editar_usuario_router

from routes.auth.login import router as login_router
from routes.auth.cambiar_pass import router as cambiar_pass_router
from routes.auth.reset_password import router as reset_password_router

from routes.bootstrap import router as bootstrap_router

from routes.general.accesos import router as accesos_router
from routes.general.bloqueo_modular import router as bloqueo_modular_router

from routes.produccion.crear_usuario_produccion import router as crear_usuario_produccion_router
from routes.produccion.obtener_usuarios_produccion import router as obtener_usuarios_produccion_router
from routes.produccion.editar_usuario_produccion import router as editar_usuario_produccion_router
from routes.produccion.accesos_produccion import router as accesos_produccion_router

import os

from dotenv import load_dotenv
from bootstrap import bootstrap
from urllib.parse import quote_plus

from models.usuarios import Usuarios
from models.roles import Roles
from models.modulos import Modulos
from models.submodulos import Submodulos
from models.permisos import Permisos
from models.usuarios_roles import usuarios_roles
from models.rol_modulos import rol_modulos
from models.rol_submodulos import rol_submodulos
from models.antispam import Antispam
from models.usuarios_bloqueados import usuarios_bloqueados

load_dotenv()

with create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{quote_plus(os.getenv('DB_PASSWORD', ''))}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
).connect() as connection:
    connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}"))
    print(f"✓ Base de datos '{os.getenv('DB_NAME')}' verificada o creada exitosamente")

db.Base.metadata.drop_all(bind=db.engine)
db.Base.metadata.create_all(bind=db.engine)
cargar_datos_iniciales()

bootstrap()

app = FastAPI(title="API INTRANET AUTH", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios_router)
app.include_router(roles_router)
app.include_router(data_usuarios_router)
app.include_router(deshabilitar_usuario_router)
app.include_router(habilitar_usuario_router)
app.include_router(crear_o_editar_usuario_router)
app.include_router(login_router)
app.include_router(cambiar_pass_router)
app.include_router(reset_password_router)
app.include_router(bootstrap_router)
app.include_router(recuperacion_check_router)
app.include_router(accesos_router)
app.include_router(crear_usuario_produccion_router)
app.include_router(obtener_usuarios_produccion_router)
app.include_router(editar_usuario_produccion_router)
app.include_router(accesos_produccion_router)
app.include_router(bloqueo_modular_router)