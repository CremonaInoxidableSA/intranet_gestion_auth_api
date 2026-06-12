from sqlalchemy import Table, Column, Integer, ForeignKey
from config.db import Base

rol_submodulos = Table(
    "rol_submodulos",
    Base.metadata,
    Column("rol_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("submodulo_id", Integer, ForeignKey("submodulos.id", ondelete="CASCADE"), primary_key=True),
    Column("permiso_id", Integer, ForeignKey("permisos.id", ondelete="CASCADE"), nullable=True),
)
