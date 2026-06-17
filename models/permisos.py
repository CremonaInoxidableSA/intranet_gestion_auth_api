from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.db import Base


class Permisos(Base):
    __tablename__ = "permisos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    prioridad = Column(Integer, nullable=False, unique=True)

    # relationships (optional) — roles link via association tables
    def __repr__(self):
        return f"<Permisos id={self.id} nombre={self.nombre} prioridad={self.prioridad}>"
