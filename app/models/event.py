from pydantic import field_validator  #per definire modelli di dati con validazione automatica
from datetime import datetime #importa la classe datetime per rappresentare date e orari
from sqlmodel import SQLModel, Field #la classe SQLModel per i modelli ORM/Pydantic, Field per applicare dei vincoli sui dati

class EventBase(SQLModel): #superclasse da cui derivano gli altri modelli, utile per utilizzare gli attributi comuni
    title: str = Field()
    description: str = Field()
    date: datetime = Field()
    location: str = Field()

    @field_validator("date", mode="before") #metodo che viene eseguito prima della validazione del campo date
    def parse_date(cls, value):
        #se la data arriva come stringa formato ISO con Z finale, la Z viene sostituita da +00.00 perché datetime.fromisoformat() non accetta la z
        if isinstance(value, str):
            cleaned = value.rstrip("Z") + "+00:00"
            return datetime.fromisoformat(cleaned)
        return value

class Event(EventBase, table=True):  #Definizione della classe Event. Diventa sia un modello Pydantic sia un mappatura di tabella ORM.
    #table=True specifica che si tratta di un modello relazionale, oltre che di un modello Pydantic -> Dice a SQLModel di generare anche la tabella corrispondente del database.
    id: int = Field(default=None, primary_key=True) #id è la chiave primaria

class EventCreate(EventBase): #Schema per creare un nuovo evento tramite API. Non include ID perché il client non deve fornirlo, verrà generato dal DB.
    pass

class EventPublic(Event): #Schema per restituire le info di un evento. Include id.
    pass
