from fastapi import APIRouter, Path, HTTPException #Usiamo la classe APIRouter al posto di FastAPI quando costruiamo parti modulari dell'app. Path serve per specificare i parametri nell'URL. HTTPException per gestire le eccezioni.
from sqlmodel import select, delete #select e delete sono funzioni di costruzione/eliminazione delle query di SQLModel
from app.data.db import SessionDep #SessionDep è un alias di tipo per l’iniezione di dipendenza di FastAPI. Per aprire e chiudere automaticamente una Session (connetterci al DB)
from app.models.event import Event, EventCreate, EventPublic
from typing import Annotated #per annotare i tipi
from app.models.registration import Registration #import necessario per usare la classe Registration definita nel package models nel file python registration.py
from app.models.user import User #import necessario per usare la classe User definita nel package models nel file python user.py

router = APIRouter(prefix="/events", tags=["events"]) #Inizializzazione del router.Tutti gli endpoint definiti saranno sotto il path /events. Il tag "events" sarà utilizzato nella documentazione Swagger

@router.get("/") #Decoratore che specifica il metodo HTTP e il percorso. Definisce l'endpoint GET /events
def get_all_events(session: SessionDep)->list[EventPublic]: #endpoint/path function, restituisce una lista di oggetti EventPublic
    """Returns the list of available events""" #questa descrizione appare nella documentazione /docs
    events = session.exec(select(Event)).all() #eseguiamo una query che seleziona tutti gli eventi
    return events



@router.get("/{id}") #Decoratore che specifica il metodo HTTP e il percorso. Definisce l'endpoint GET /events/{id}
def get_event( #endpoint/path function, restituisce un oggetto EventPublic
        session: SessionDep,
        id: Annotated[int, Path(description="The id of the event to get")]
)->EventPublic:
    """Returns the event with the given ID""" #questa descrizione appare nella documentazione /docs
    event = session.get(Event, id) #Cerca l'evento con l'ID dato
    if not event: #se l'evento non è esiste, viene sollevata un'eccezione
        raise HTTPException(status_code=404, detail=f"The event with ID {id} was not found") #404->la risorsa richiesta (l'evento con l'ID cercato) non esiste
    return event


@router.post("/") #Decoratore che specifica il metodo HTTP e il percorso. Definisce l'endpoint POST /events
def add_event(session: SessionDep, event: EventCreate): #Endpoint/path function
    #event: EventCreate dice a FastAPI di aspettarsi un oggetto JSON nel body della richiesta e di convertirlo automaticamente in un oggetto EventCreate utilizzando Pydantic
    """Adds a new event to the database""" #questa descrizione appare nella documentazione /docs
    session.add(Event.model_validate(event)) #aggiunge l'oggetto alla sessione del DB
    session.commit() #funzione che rende effettive le modifiche al DB (altrimenti le perderemmo al termine della sessione)
    return "Event successfully added"

@router.put("/{id}") #Decoratore che specifica il metodo HTTP e il percorso. Definisce l'endpoint PUT /events/{id}
def update_event( #Endpoint/path function
        session: SessionDep,
        id: Annotated[int, Path(description="The id of the event to update")],
        #Il tipo atteso per l'id è un intero. Path aggiunge una descrizione visibile nella documentazione Swagger.
        new_event: EventCreate #Il nuovo contenuto dell'evento viene ricevuto nel corpo della richiesta come oggetto EventCreate
):
    """Updates the event with the given ID""" #questa descrizione appare nella documentazione /docs
    event = session.get(Event, id) #cerca nel database l'evento con l'ID fornito
    if not event: #se non esiste nessun evento con l'ID fornito, rende error 404 -> la risorsa richiesta (l'evento con l'ID cercato) non esiste
        raise HTTPException(status_code=404, detail="Event not found") #e viene sollevata un'eccezione
    event.title = new_event.title #se l'evento esiste aggiorna i suoi campi con quelli forniti
    event.description = new_event.description
    event.date = new_event.date
    event.location = new_event.location
    session.add(event) #aggiorna l'oggetto che è stato modificato
    session.commit() #funzione che rende effettive le modifiche al DB (altrimenti le perderemmo al termine della sessione
    return "Event successfully updated"

@router.delete("/") #Decoratore che specifica il metodo HTTP e il percorso. Definisce l'endpoint DELETE /events
def delete_all_events(session: SessionDep): #endpoint/path function
    """Delete all events""" #questa descrizione appare nella documentazione /docs
    session.exec(delete(Registration))  #Rimuovo le registrazioni agli eventi
    session.exec(delete(Event)) #eseguiamo una query di cancellazione SQL -> elimina tutti i record dalla tabella Event
    session.commit() #funzione che rende effettive le modifiche al DB (altrimenti le perderemmo al termine della sessione)
    return "All events successfully deleted"


@router.delete("/{id}") #Decoratore che specifica il metodo HTTP e il percorso. Definisce l'endpoint DELETE /events/{id}
def delete_event_by_id( #endpoint/path function
        session: SessionDep,
        id: int
):
    """Delete the event with the given id""" #questa descrizione appare nella documentazione /docs
    event = session.get(Event, id) #cerca nel database l'evento con l'ID fornito
    if not event:  #se l'evento non esiste, solleva un'eccezione
        raise HTTPException(status_code=404, detail=f"The event with ID {id} was not found") #404->la risorsa richiesta (l'evento) non esiste
    session.exec(delete(Registration).where(Registration.event_id == id)) #elimina la registrazione associata all'evento
    session.delete(event) #se l'evento esiste, lo elimina
    session.commit() #funzione che rende effettive le modifiche al DB (altrimenti le perderemmo al termine della sessione)
    return f"Event with ID {id} successfully deleted"


@router.post("/{id}/register") #Decoratore che specifica il metodo HTTP e il percorso. Definisce l'endpoint POST /events/{id}/register
def register_for_event( #endpoint/path function
        session: SessionDep,
        id: Annotated[int, Path(description="The id of the event the user wants to register for")],
        user: User): #passo l'utente nel body della richiesta
    """Register a user to the event with the given ID"""
    event = session.get(Event, id) #cerca nel database l'evento con l'ID fornito
    if not event: #se l'evento non esiste, solleva un'eccezione
        raise HTTPException(status_code=404, detail="Event not found") #404->la risorsa richiesta non esiste
    db_user = session.get(User, user.username) #cerca nel database l'utente con il dato username
    if not db_user: #se l'utente non esiste viene creato
        db_user = user
        session.add(db_user)
        session.commit() #funzione che rende effettive le modifiche al DB (altrimenti le perderemmo al termine della sessione)
    registration = Registration(username=db_user.username, event_id=id) #creiamo un oggetto che collega l'utente all'evento tramite username ed event_id
    session.add(registration) #aggiunge la registrazione alla sessione del DB
    try:
        session.commit() #funzione che rende effettive le modifiche al DB (altrimenti le perderemmo al termine della sessione)
    except Exception:
        raise HTTPException(status_code=400, detail="Registration failed") #400->Bad Request
    return "User registered successfully"
