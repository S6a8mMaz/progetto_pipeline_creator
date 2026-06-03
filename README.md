# Pipeline Creator

Applicazione per la costruzione guidata di pipeline di processamento dati.

## Esecuzione locale

Scaricare il progetto da GitHub, estrarre il file `.zip` ed eseguire gli script nella cartella principale del progetto.

### 1. Setup

Su Windows eseguire:

```bat
Setup_valDB_windows.bat
```

Lo script:
- verifica la presenza di Python 3.10;
- crea la virtual environment `venv`;
- installa le librerie con le versioni definite in `requirements.txt`;
- crea le tabelle del database SQLite;
- chiede se popolare il database con dati iniziali di esempio.

### 2. Avvio applicazione

Dopo il setup, eseguire:

```bat
Start_app_windows.bat
```

Lo script avvia:
- backend FastAPI;
- frontend Streamlit.

Interfaccia utente:

```text
http://localhost:8501
```

Documentazione API:

```text
http://127.0.0.1:8000/docs
```

## Tecnologie utilizzate (e scaricate dallo script)

| Tecnologia | Versione | Utilizzo |
|---|---:|---|
| Python | 3.10.11 | Linguaggio principale |
| FastAPI | 0.136.3 | Backend REST API |
| Uvicorn | 0.48.0 | Server ASGI |
| Streamlit | 1.58.0 | Interfaccia web |
| SQLAlchemy | 2.0.50 | ORM database |
| Requests | 2.34.2 | Chiamate HTTP frontend-backend |
| Pydantic | 2.13.4 | Validazione dati e schemi |
| SQLite | 3.40.1 | Database locale |
| Windows | 10.0.26200.8457 | Ambiente di sviluppo/test |
