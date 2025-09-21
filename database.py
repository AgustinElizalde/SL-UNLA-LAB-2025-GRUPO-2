from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Time, create_engine
from sqlalchemy.orm import relationship, declarative_base
from datetime import date

engine = create_engine('sqlite:///mi_base.db', echo=True)
Base = declarative_base()

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    dni = Column(String, unique=True, nullable=False)
    telefono = Column(String, nullable=True)
    fecha_nacimiento = Column(Date, nullable=False)
    habilitado = Column(Boolean, default=True)

    # Relación con Turnos
    turnos = relationship("Turno", back_populates="cliente")

class Turno(Base):
    __tablename__ = "turnos"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    estado = Column(String, default="pendiente")  # pendiente, confirmado, cancelado
    cliente_id = Column(Integer, ForeignKey("clientes.id"))

    # Relación con Cliente
    cliente = relationship("Cliente", back_populates="turnos")