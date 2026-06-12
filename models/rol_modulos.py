from sqlalchemy import Table, Column, Integer, ForeignKey
from config.db import Base

rol_modulos = Table(
    "rol_modulos",
    Base.metadata,
    Column("rol_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("modulo_id", Integer, ForeignKey("modulos.id", ondelete="CASCADE"), primary_key=True),
    Column("permiso_id", Integer, ForeignKey("permisos.id", ondelete="CASCADE"), nullable=True),
)