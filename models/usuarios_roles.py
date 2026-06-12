from sqlalchemy import Table, Column, Integer, ForeignKey
from config.db import Base

usuarios_roles = Table(
    "usuarios_roles",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
    Column("rol_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)
