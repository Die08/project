from fastapi import APIRouter, Path, HTTPException #Usiamo la classe APIRouter al posto di FastAPI quando costruiamo parti modulari dell'app. Path serve per specificare i parametri nel URL. HTTPException per gestire le eccezioni.
from sqlmodel import select, delete #select e delete sono funzioni di costruzione/eliminazione delle query di SQLModel
from typing import Annotated #per annotare i tipi
from app.data.db import SessionDep #SessionDep è un alias di tipo per l’iniezione di dipendenza di FastAPI. Per aprire e chiudere automaticamente una Session (connetterci al DB)
from app.models.registration import Registration #import necessario per usare la classe Registration definita nel package models nel file python registration.py
from app.models.user import User, UserCreate #import necessario per usare la classe User definita nel package models nel file python user.py

router = APIRouter(prefix="/users", tags=["users"]) #Inizializzazione del router.Tutti gli endpoint definiti saranno sotto il path /users. Il tag "users" sarà utilizzato nella documentazione Swagger


@router.get("/") #Decoratore che specifica il metodo HTTP e il percorso. Definisce l'endpoint GET /users
def get_all_users(session: SessionDep)->list[User]:  #endpoint/path function, restituisce una lista di oggetti User
    """Returns the list of all users""" #questa descrizione appare nella documentazione /docs
    users = session.exec(select(User)).all() #eseguiamo una query che seleziona tutti gli utenti
    return users

@router.get("/{username}") #Decoratore che specifica il metodo HTTP e il percorso. Definisce l'endpoint GET /users/{id}
def get_user_by_username( #endpoint/path function, restituisce oggetto User
        session: SessionDep,
        username: Annotated[str, Path(description="The username of the user to get")]
)->User:
    """Returns the user with the given username""" #questa descrizione appare nella documentazione /docs
    user = session.get(User, username) #Cerca l'utente con lo username dato
    if not user: #se l'utente non esiste viene sollevata un'eccezione
        raise HTTPException(status_code=404, detail="User not found") #404->la risorsa richiesta (l'utente con lo username cercato) non esiste
    return user

@router.post("/") #Decoratore che specifica il metodo HTTP e il percorso. Definisce l'endpoint POST /users
def add_user(session: SessionDep, user: UserCreate): #Endpoint/path function
    """Adds a new user""" #questa descrizione appare nella documentazione /docs
    existing = session.get(User, user.username) #Cerca l'utente con lo username dato
    if existing: #se esiste già uno username con lo username dato viene sollevata un'eccezione
        raise HTTPException(status_code=409, detail="User already exists") #409 -> Conflict
    session.add(User.model_validate(user)) #aggiunge l'oggetto alla sessione del DB
    session.commit() #funzione che rende effettive le modifiche al DB (altrimenti le perderemmo al termine della sessione)
    return "User successfully added"

@router.delete("/") #Decoratore che specifica il metodo HTTP e il percorso. Definisce l'endpoint DELETE /users
def delete_all_users(session: SessionDep): #endpoint/path function
    """Delete all users""" #questa descrizione appare nella documentazione /docs
    session.exec(delete(Registration))  #Rimuovo le registrazioni degli utenti
    session.exec(delete(User))  # eseguiamo una query di cancellazione SQL -> elimina tutti i record dalla tabella User
    session.commit() #funzione che rende effettive le modifiche al DB (altrimenti le perderemmo al termine della sessione)
    return "All users successfully deleted"

@router.delete("/{username}") #Decoratore che specifica il metodo HTTP e il percorso. Definisce l'endpoint DELETE /users/{id}
def delete_user_by_username( #endpoint/path function
        session: SessionDep,
        username: Annotated[str, Path(description="The username of the user to delete")] #Il tipo atteso per lo username è una stringa. Path aggiunge una descrizione visibile nella documentazione Swagger.
):
    """Delete the user with the given username""" #questa descrizione appare nella documentazione /docs
    user = session.get(User, username) #cerca nel database l'utente con lo username fornito
    if not user: #se l'utente non esiste solleva un'eccezione
        raise HTTPException(status_code=404, detail="User not found") #404->la risorsa richiesta (l'utente) non esiste
    session.exec(delete(Registration).where(Registration.username == username)) #elimina la registrazione associata all'utente
    session.delete(user) #se l'utente esiste, lo elimina
    session.commit() #funzione che rende effettive le modifiche al DB (altrimenti le perderemmo al termine della sessione)
    return f"User with username {username} successfully deleted"
