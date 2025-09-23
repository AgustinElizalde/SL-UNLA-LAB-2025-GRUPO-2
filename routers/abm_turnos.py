from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from datetime import date, time, datetime, timedelta
from pydantic import BaseModel
from database import Base, Turno, engine, Cliente

# Crear tablas
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

# Dependencia para obtener DB
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

class TurnoCreate(BaseModel):
    fecha: date
    hora: time
    estado: str = "pendiente"
    cliente_id: int

class TurnoUpdate(BaseModel):
    fecha: date | None = None
    hora: time | None = None
    estado: str | None = None
    cliente_id: int | None = None

# ---------------- Endpoints ----------------

# Crear turno
@router.post("/turnos")
def crear_turno(turno: TurnoCreate, db: Session = Depends(get_db)):

    # Validar que no exista un turno en la misma fecha y hora
    turno_existente = db.query(Turno).filter(
        Turno.fecha == turno.fecha,
        Turno.hora == turno.hora,
        Turno.estado != "cancelado" 
    ).first()

    cliente = db.query(Cliente).filter(Cliente.id == turno.cliente_id).first()

    if not cliente.habilitado:
        raise HTTPException(status_code=400, detail="El cliente no está habilitado para sacar turnos")

    if turno_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Ya hay un turno tomado el {turno.fecha} a las {turno.hora}"
        )

    hoy = datetime.now().date()
    hace_6_meses = hoy - timedelta(days=180)

    turnos_cancelados = db.query(Turno).filter(
        Turno.cliente_id == turno.cliente_id,
        Turno.estado == "cancelado",
        Turno.fecha >= hace_6_meses.strftime("%Y-%m-%d")
    ).count()

    if turnos_cancelados >= 5:
        raise HTTPException(
            status_code=400,
            detail="El cliente no puede tomar un nuevo turno porque tiene 5 o más turnos cancelados en los últimos 6 meses"
        )
    
    nuevo = Turno(
        fecha=turno.fecha,
        hora=turno.hora,
        estado=turno.estado,
        cliente_id=turno.cliente_id
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# Listar todos los turnos
@router.get("/turnos")
def listar_turnos():
    db = next(get_db())
    turnos = db.query(Turno).all()
    return [{"id": t.id, "fecha": str(t.fecha), "hora": str(t.hora), "estado": t.estado} for t in turnos]

# Obtener turno por id
@router.get("/turnos/{id}")
def obtener_turno(id: int):
    db = next(get_db())
    t = db.query(Turno).filter(Turno.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    return {"id": t.id, "fecha": str(t.fecha), "hora": str(t.hora), "estado": t.estado, "cliente_id": t.cliente_id}

# Actualizar turno
@router.put("/turnos")
def actualizar_turno(id: int, turno: TurnoUpdate, db: Session = Depends(get_db)):
    t = db.query(Turno).filter(Turno.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    for attr, value in turno.dict(exclude_unset=True).items():
        setattr(t, attr, value)

    db.commit()
    db.refresh(t)
    return t

# Eliminar turno
@router.patch("/turnos")
def cancelar_turno(id: int, db: Session = Depends(get_db)):
    turno = db.query(Turno).filter(Turno.id == id).first()

    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    turno.estado = "cancelado"
    db.commit()
    db.refresh(turno)

    return {
        "detail": f"El turno con id {id} fue cancelado",
        "id": turno.id,
        "fecha": turno.fecha,
        "hora": turno.hora,
        "estado": turno.estado,
        "cliente_id": turno.cliente_id
    }
