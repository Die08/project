from app.config import config
from pathlib import Path
import os

if Path(__file__).parent == Path(os.getcwd()):
    config.root_dir = "."
#in sostanza, questa condizione serve a correggere il percorso delle risorse
#statiche/database nel caso in cui qualcuno faccia partire l’app in modo “non standard”

from fastapi import FastAPI
from app.routers import frontend, events, users, registrations
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.data.db import init_database

@asynccontextmanager
async def lifespan(_: FastAPI):
    # on start
    init_database() # apre la connessione al database, crea eventuali tabelle mancanti e applica migrazioni
    yield  #FastAPI resta in ascolto delle richieste.
    # on close

app = FastAPI(lifespan=lifespan)
app.mount(
    "/static",
    StaticFiles(directory=config.root_dir / "static"),
    name="static"
)

#Registriamo le API definite nei vari moduli
app.include_router(frontend.router)
app.include_router(events.router)
app.include_router(users.router)
app.include_router(registrations.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
