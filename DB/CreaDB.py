from DB.ConfigDB import Base
from DB.ConfigDB import engine
from DB import EntitaSQL_db


def CreaDB(): # Crea fisicamente tutte le tabelle definite nei modelli ORM
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__": # Esegue l'inizializzazione del database se il file è lanciato direttamente
    CreaDB()

    print("\n\t*** Database e tabelle creati correttamente ***\n")

# Per creare il Database e le tabelle vuote --> python -m DB.CreaDB