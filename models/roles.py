from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from config.db import Base
from .usuarios_roles import usuarios_roles
from .rol_modulos import rol_modulos
from .rol_submodulos import rol_submodulos


class Roles(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    puede_habilitar = Column(Boolean, nullable=False, default=False)
    puede_consultar = Column(Boolean, nullable=False, default=False)

    usuarios = relationship("Usuarios", secondary=usuarios_roles, back_populates="roles")
    modulos = relationship("Modulos", secondary=rol_modulos, back_populates="roles")
    submodulos = relationship("Submodulos", secondary=rol_submodulos, back_populates="roles")