from fastapi import FastAPI
from routers import abm_turnos, alta_cliente 

app = FastAPI()

app.include_router(abm_turnos.router)
app.include_router(alta_cliente.router)

@app.get("/")
def root():
    return {"message": "API funcionando 🚀"}
