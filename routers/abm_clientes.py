from fastapi import APIRouter, Depends, HTTPException
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

# ------------------- Schemas -------------------
class ClienteCreate(BaseModel):
    nombre: str
    email: str
    dni: str
    telefono: str | None = None
    fecha_nacimiento: str  # string en formato "YYYY-MM-DD"
    habilitado: bool = True

class ClienteUpdate(BaseModel):
    nombre: str | None = None
    email: str | None = None
    dni: str | None = None
    telefono: str | None = None
    fecha_nacimiento: str | None = None
    habilitado: bool | None = None


# ------------------- Endpoints -------------------

#-------------------- Calculo de edad -------------
def calcular_edad(fecha_nacimiento: date) -> int:
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )

# Crear cliente
@router.post("/clientes")
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    f = date.fromisoformat(cliente.fecha_nacimiento)

    dni_existente = db.query(Cliente).filter(Cliente.dni == cliente.dni).first()
    email_existente = db.query(Cliente).filter(Cliente.email == cliente.email).first()

    if dni_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un cliente con el DNI {cliente.dni}"
        )

    if email_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un cliente con el mismo email {cliente.email}"
        )

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
        "habilitado": nuevo.habilitado,
        "edad": calcular_edad(nuevo.fecha_nacimiento)
    }

# Listar todos los clientes
@router.get("/clientes")
def listar_clientes(db: Session = Depends(get_db)):
    clientes = db.query(Cliente).all()
    return [
        {
            "id": c.id,
            "nombre": c.nombre,
            "email": c.email,
            "dni": c.dni,
            "telefono": c.telefono,
            "fecha_nacimiento": str(c.fecha_nacimiento),
            "habilitado": c.habilitado,
            "edad": calcular_edad(c.fecha_nacimiento)
        }
        for c in clientes
    ]

# Obtener un cliente por ID
@router.get("/clientes/{id}")
def obtener_clientes(id: int | None = None, db: Session = Depends(get_db)):
    if id:
        c = db.query(Cliente).filter(Cliente.id == id).first()
        if not c:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return c
    return db.query(Cliente).all()

# Actualizar cliente
@router.put("/clientes")
def actualizar_cliente(id: int, datos: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    if datos.nombre is not None:
        cliente.nombre = datos.nombre
    if datos.email is not None:
        cliente.email = datos.email
    if datos.dni is not None:
        cliente.dni = datos.dni
    if datos.telefono is not None:
        cliente.telefono = datos.telefono
    if datos.fecha_nacimiento is not None:
        cliente.fecha_nacimiento = date.fromisoformat(datos.fecha_nacimiento)
    if datos.habilitado is not None:
        cliente.habilitado = datos.habilitado

    db.commit()
    db.refresh(cliente)

    return {
        "id": cliente.id,
        "nombre": cliente.nombre,
        "email": cliente.email,
        "dni": cliente.dni,
        "telefono": cliente.telefono,
        "fecha_nacimiento": str(cliente.fecha_nacimiento),
        "habilitado": cliente.habilitado,
        "edad": calcular_edad(cliente.fecha_nacimiento)
    }

# Eliminar cliente
@router.delete("/clientes")
def eliminar_cliente(id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db.delete(cliente)
    db.commit()

    return {"mensaje": f"Cliente con ID {id} eliminado correctamente"}
