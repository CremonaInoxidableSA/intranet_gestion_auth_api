from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, text
from sqlalchemy.orm import relationship
from config.db import Base


class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tabla = Column(String(100), nullable=False)
    registro_id = Column(Integer, nullable=False)
    accion = Column(Enum("INSERT", "UPDATE", "DELETE", name="auditoria_accion"), nullable=False)
    datos_viejos = Column(JSON, nullable=True)
    datos_nuevos = Column(JSON, nullable=True)
    fecha = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    usuario = relationship("Usuarios")
