from fastapi import FastAPI
from routers import abm_turnos, abm_clientes 

app = FastAPI()

app.include_router(abm_turnos.router)
app.include_router(abm_clientes.router)

@app.get("/")
def root():
    return {"message": "API funcionando"}
