from sqlalchemy import Column, Integer, String, DateTime
from config.db import Base


class Antispam(Base):
    __tablename__ = "antispam"

    id = Column(Integer, primary_key=True, autoincrement=True)
    accion = Column(String(100), nullable=False)
    fecha = Column(DateTime, nullable=False)
    correo = Column(String(100), nullable=False)