from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from config.db import Base


class Sesiones(Base):
    __tablename__ = "sesiones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(512), nullable=False, unique=True)
    ip_origen = Column(String(45), nullable=True)
    equipo = Column(String(255), nullable=True)
    iniciada = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    expira = Column(DateTime, nullable=False)

    usuario = relationship("Usuarios")
