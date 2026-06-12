from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.db import Base
from .roles import rol_modulos


class Modulos(Base):
    __tablename__ = "modulos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    path = Column(String(255), nullable=False, unique=True)

    submodulos = relationship("Submodulos", back_populates="modulo", cascade="all, delete-orphan")
    roles = relationship("Roles", secondary=rol_modulos, back_populates="modulos")