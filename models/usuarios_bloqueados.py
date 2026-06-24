from sqlalchemy import Table, Column, Integer, ForeignKey, Boolean
from config.db import Base

usuarios_bloqueados = Table(
    "usuarios_bloqueados",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
    Column("modulo_id", Integer, ForeignKey("modulos.id", ondelete="CASCADE"), primary_key=True),
    Column("bloqueado", Boolean, nullable=False, default=False)
)