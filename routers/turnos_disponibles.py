from fastapi import Query, APIRouter, Depends, HTTPException
from datetime import datetime, time, timedelta
from database import Base, Turno, engine
from sqlalchemy.orm import Session, sessionmaker
from .generador_de_turnos import generador_turnos

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

@router.get("/turnos-disponibles")
def turnos_disponibles(fecha: str = Query(...), db: Session = Depends(get_db)):
    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    # Consultar turnos ocupados (no cancelados)
    turnos_ocupados = (
        db.query(Turno)
        .filter(Turno.fecha == fecha_obj, Turno.estado != "cancelado")
        .all()
    )
    ocupados = {t.hora.strftime("%H:%M") for t in turnos_ocupados}

    # Filtrar horarios disponibles
    horarios_disponibles = [h for h in generador_turnos if h not in ocupados]

    return {
        "fecha": str(fecha_obj),
        "horarios_disponibles": horarios_disponibles
    }
