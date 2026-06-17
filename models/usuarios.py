from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from config.db import Base
from .usuarios_roles import usuarios_roles


class Usuarios(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    username = Column(String(100), nullable=True, unique=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=True)
    habilitado = Column(Boolean, nullable=False, default=True)
    legajo = Column(Integer, nullable=False)
    dni = Column(Integer, nullable=True)
    cambiar_contra = Column(Boolean, nullable=False, default=False)

    roles = relationship("Roles", secondary=usuarios_roles, back_populates="usuarios")