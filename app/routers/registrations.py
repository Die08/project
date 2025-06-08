from fastapi import APIRouter, HTTPException, Query #Usiamo la classe APIRouter al posto di FastAPI quando costruiamo parti modulari dell'app. Path serve per specificare i parametri nel URL. HTTPException per gestire le eccezioni.
from sqlmodel import select #select è una funzione di costruzione delle query di SQLModel
from typing import Annotated #per annotare i tipi
from app.data.db import SessionDep #SessionDep è un alias di tipo per l’iniezione di dipendenza di FastAPI. Per aprire e chiudere automaticamente una Session (connetterci al DB)
from app.models.registration import Registration #import necessario per usare la classe Registration definita nel package models nel file python registration.py

router = APIRouter(prefix="/registrations", tags=["registrations"]) #Inizializzazione del router.Tutti gli endpoint definiti saranno sotto il path /registrations. Il tag "registrations" sarà utilizzato nella documentazione Swagger

@router.get("/") #Decoratore che specifica il metodo HTTP e il percorso. Definisce l'endpoint GET /registrations
def get_registrations(session: SessionDep)->list[Registration]: #endpoint/path function, restituisce una lista di oggetti Registration
    """Returns the list of all registrations"""
    registration = session.exec(select(Registration)).all() #eseguiamo una query che seleziona tutte le registrazioni
    return registration

@router.delete("/") #Decoratore che specifica il metodo HTTP e il percorso. Definisce l'endpoint DELETE /registrations
def delete_registration_by_username_and_event_id( #endpoint/path function
        event_id: Annotated[int, Query(description="The id of the event to delete")], #Il tipo atteso per l'id è un intero. Path aggiunge una descrizione visibile nella documentazione Swagger.
        username: Annotated[str, Query(description="The username of the person to delete")],
        session: SessionDep
):
    """Delete the registration with the given ID and the given username""" #questa descrizione appare nella documentazione /docs
    registration = session.exec( #eseguiamo una query che seleziona tutte le registrazioni con lo username dato e l'ID evento dato
        select(Registration).where(
            Registration.username == username,
            Registration.event_id == event_id
        )
    ).first()
    if not registration: #se la registrazione non esiste
        raise HTTPException(status_code=404, detail="Registration not found") #error 404-> la risorsa richiesta (la registrazione) non esiste
    session.delete(registration) #Rimuovo le registrazioni
    session.commit() #funzione che rende effettive le modifiche al DB (altrimenti le perderemmo al termine della sessione)
    return f"Registration of {username} for event {event_id} deleted successfully"
