from sqlmodel import create_engine, SQLModel, Session
#Create_engine: funzione per creare una connessione al database
#SQLModel: classe base da cui derivare i modelli che rappresentano le tabelle nel database
#Session: oggetto per aprire una "sessione" sul database
from typing import Annotated #per annotare tipi
from fastapi import Depends #per dichiarare dipendenze nei path operation di FastAPI
import os #libreria standard di Python per operazioni sul filesystem
from faker import Faker #Libreria per generare dati fittizi con cui riempire in database. Utili sopratutto in fase di test.
from app.config import config
# TODO: remember to import all the DB models here
from app.models.registration import Registration  #import necessario per utilizzare la classe Registration definita nel package models nel file python registration.py
from app.models.user import User #import necessario per usare la classe User definita nel package models nel file python user.py
from app.models.event import Event #import necessario per usare la classe Event definita nel package models nel file python event.py

sqlite_file_name = config.root_dir / "data/database.db" #Costruisce il percorso assoluto al file del database basandosi sulla root del progetto
sqlite_url = f"sqlite:///{sqlite_file_name}" #crea la stringa URL di connessione al database
connect_args = {"check_same_thread": False} #per applicazioni multithread
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True) #crea il motore di connessione al database: specifica dove si trova il database, le opzioni di connessione, echo=True: fa in modo che ogni query SQL venga stampata sulla console (utile per il debug).
#Una volta creato l’engine, potremo usarlo per: creare le tabelle, aprire sessioni, eseguire query (lettura, scrittura, modifica, cancellazione dati).

def init_database() -> None: #Funzione che inizializza il database creando tutte le tabelle definite nei modelli SQLModel
    ds_exists = os.path.isfile(sqlite_file_name) #controllo se il file del database esiste già
    SQLModel.metadata.create_all(engine) #crea le tabelle nel database in base ai modelli definiti
    if not ds_exists: #se il database è nuovo crea un oggetto Faker per generare dati causali e apre una session per popolarlo
        f = Faker("it_IT") #generatore di dati finti in italiano
        with Session(engine) as session: #Apre una sessione al database usando il contesto with, che si chiude automaticamente alla fine. Engine è il motore di connessione al DB. Session permette di eseguire operazioni sul database
            # TODO: (optional) initialize the database with fake data
            for i in range(10):  #ciclo che verrà eseguito 10 volte, per ogni iterazione viene creato un utente fittizio
                user = User(username=f.username(), name=f.name(), email=f.email())
                session.add(user) #aggiunge l'utente creato alla sessione del database
            session.commit()  #salva tutte le modifiche fatte nella sessione
            for i in range(10):  #ciclo che verrà eseguito 10 volte, per ogni iterazione viene creato un evento fittizio
                event = Event(title=f.sentence(nb_words=5), description=f.sentence(nb_words=5), date=f.date_time(), location=f.sentence(nb_words=2))
                session.add(event) #aggiunge l'evento creato alla sessione del database
            session.commit()  #salva tutte le modifiche fatte nella sessione
            for i in range(10):  #ciclo che verrà eseguito 10 volte, per ogni iterazione viene creata una registrazione fittizia
                registration = Registration(username=f.username(), event_id=f.pyint(1, 10))
                session.add(registration) #aggiunge la registrazione creata alla sessione del database
            session.commit()  #salva tutte le modifiche fatte nella sessione


def get_session(): #Funzione che restituisce una nuova istanza di DB ogni volta che verrà chiamata e la terrà aperta per tutto il tempo necessario (grazie all'uso di yield)
    with Session(engine) as session:
        yield session #Restituisce la sessione all’endpoint che ne ha bisogno. Dopo il completamento della richiesta, FastAPI riprende l’esecuzione dopo il yield, chiudendo la sessione.


SessionDep = Annotated[Session, Depends(get_session)] #alias di tipo che incapsula sia il tipo (Session) sia la logica per crearlo (Depends(get_session)).
