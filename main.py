from fastapi import FastAPI
from routers import abm_turnos, abm_clientes, turnos_disponibles, generador_de_turnos

app = FastAPI()

app.include_router(abm_turnos.router)
app.include_router(abm_clientes.router)
app.include_router(turnos_disponibles.router)

@app.get("/")
def root():
    return {"message": "API funcionando"}
