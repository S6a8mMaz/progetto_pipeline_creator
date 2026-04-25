from sqlalchemy import create_engine  # Funzione per creare il motore DB
from sqlalchemy.orm import sessionmaker  # Factory per creare sessioni DB
from sqlalchemy.orm import declarative_base  # Base per modelli ORM
import os  # Per leggere variabili d'ambiente

print("\n\t*** DB PATH:", os.path.abspath("PIPELINE_CREATOR_DB.db"), "***\n")

SQLALCHEMY_DATABASE_URL = os.getenv(  # URL del database configurabile
    "DATABASE_URL",  # Variabile d'ambiente opzionale
    "sqlite:///./PIPELINE_CREATOR_DB.db"  # Default: SQLite locale
)

engine = create_engine(  # Crea il motore del database
    SQLALCHEMY_DATABASE_URL,  # URL di connessione
    connect_args={"check_same_thread": False},  # Necessario per SQLite con thread multipli (FastAPI)
    echo=False  # Imposta True per debug SQL (opzionale)
)

SessionLocal = sessionmaker(  # Factory per creare sessioni DB
    autocommit=False,  # Le modifiche non sono salvate automaticamente
    autoflush=False,   # Non esegue flush automatico
    bind=engine        # Collega le sessioni all'engine
)

Base = declarative_base()  # Classe base per tutti i modelli ORM


def get_db():  # Dependency per ottenere una sessione DB (usata nelle API)
    db = SessionLocal()  # Crea una nuova sessione
    try:
        yield db  # Restituisce la sessione
    finally:
        db.close()  # Chiude sempre la sessione (evita leak)


def init_db():  # Inizializza il database creando tutte le tabelle
    Base.metadata.create_all(bind=engine)  # Crea le tabelle se non esistono