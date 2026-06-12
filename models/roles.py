from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base
from .permisos import Permisos


# Association tables (moved here from models/associations.py)
usuarios_roles = Table(
    "usuarios_roles",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
    Column("rol_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


rol_modulos = Table(
    "rol_modulos",
    Base.metadata,
    Column("rol_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("modulo_id", Integer, ForeignKey("modulos.id", ondelete="CASCADE"), primary_key=True),
    Column("permiso_id", Integer, ForeignKey("permisos.id", ondelete="CASCADE"), nullable=True),
)


rol_submodulos = Table(
    "rol_submodulos",
    Base.metadata,
    Column("rol_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("submodulo_id", Integer, ForeignKey("submodulos.id", ondelete="CASCADE"), primary_key=True),
    Column("permiso_id", Integer, ForeignKey("permisos.id", ondelete="CASCADE"), nullable=True),
)


class Roles(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)

    usuarios = relationship("Usuarios", secondary=usuarios_roles, back_populates="roles")
    modulos = relationship("Modulos", secondary=rol_modulos, back_populates="roles")
    submodulos = relationship("Submodulos", secondary=rol_submodulos, back_populates="roles")