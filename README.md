# Pipeline Creator
## Esecuzione dell'applicazione

Per eseguire l'applicazione in locale, scaricare il progetto da GitHub ed estrarre il file `.zip`.

All'interno della cartella scaricata, eseguire i seguenti script nel seguente ordine:

---

### 1. Setup_valDB.bat

Eseguire:

```bat
Setup_valDB.bat
```

Questo script:
- verifica la presenza di Python;
- crea l'ambiente virtuale dell'applicazione;
- scarica tutte le librerie Python necessarie;
- crea le tabelle del database;
- chiede se si desidera valorizzare il database con un esempio di contesti e dati iniziali.

---

### 2. Start_app.bat

Dopo aver completato il setup, eseguire:

```bat
Start_app.bat
```

Questo script avvia:
- il backend dell'applicazione;
- il frontend dell'applicazione.

Una volta avviata, l'applicazione sarà accessibile dal browser.

---

## Tecnologie utilizzate

| Tecnologia | Versione | Utilizzo |
|---|---:|---|
| Python | 3.10.11 | Linguaggio principale del progetto |
| FastAPI | 0.136.3 | Backend REST API |
| Uvicorn | 0.48.0 | Server ASGI per l'esecuzione del backend |
| Streamlit | 1.58.0 | Interfaccia utente web |
| SQLAlchemy | 2.0.50 | ORM per la gestione del database |
| Requests | 2.34.2 | Comunicazione HTTP tra frontend e backend |
| Pydantic | 2.13.4 | Validazione dei dati e definizione degli schemi |
| SQLite | 3.40.1 | Database locale |
| Windows | 10.0.26200.8457 | Sistema operativo utilizzato per sviluppo e test |

---

## Note

La cartella `venv` non è inclusa nel repository GitHub perché viene generata automaticamente dallo script di setup.

Il database utilizzato è SQLite e viene creato localmente all'interno della cartella del progetto.

L'applicazione è stata sviluppata e testata in ambiente Windows.
