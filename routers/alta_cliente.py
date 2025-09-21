from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from datetime import date
from pydantic import BaseModel
from database import Base, Cliente, engine   

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Configurar sesión
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Dependencia para obtener DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

# Schema Pydantic
class ClienteCreate(BaseModel):
    nombre: str
    email: str
    dni: str
    telefono: str | None = None
    fecha_nacimiento: str  # string en formato "YYYY-MM-DD"
    habilitado: bool = True

# ------------------- Endpoint -------------------
@router.post("/clientes")
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    f = date.fromisoformat(cliente.fecha_nacimiento)

    nuevo = Cliente(
        nombre=cliente.nombre,
        email=cliente.email,
        dni=cliente.dni,
        telefono=cliente.telefono,
        fecha_nacimiento=f,
        habilitado=cliente.habilitado
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {
        "id": nuevo.id,
        "nombre": nuevo.nombre,
        "email": nuevo.email,
        "dni": nuevo.dni,
        "telefono": nuevo.telefono,
        "fecha_nacimiento": str(nuevo.fecha_nacimiento),
        "habilitado": nuevo.habilitado
    }
