from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base
from .roles import rol_submodulos


class Submodulos(Base):
    __tablename__ = "submodulos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    modulo_id = Column(Integer, ForeignKey("modulos.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(100), nullable=False)
    path = Column(String(255), nullable=False, unique=True)

    modulo = relationship("Modulos", back_populates="submodulos")
    roles = relationship("Roles", secondary=rol_submodulos, back_populates="submodulos")