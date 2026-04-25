from fastapi import FastAPI
from DB.ConfigDB import engine, Base
from API.GestoreAPI import router

app = FastAPI(  # Crea applicazione FastAPI
    title="Pipeline Creator API",
    description="API per la costruzione e gestione di pipeline di processamento dati",  # Descrizione
    version="1.0.0"  # Versione API
)

@app.on_event("startup")  # Evento eseguito all'avvio del server
def on_startup():
    Base.metadata.create_all(bind=engine)  # Crea le tabelle nel database se non esistono

app.include_router(router)  # Registra tutti gli endpoint definiti nel router