from pydantic import EmailStr #per accettare stringhe con un formato email valido
from sqlmodel import SQLModel, Field #la classe SQLModel per i modelli ORM/Pydantic, Field per applicare dei vincoli sui dati

class User(SQLModel, table=True): #Definizione della classe User. Diventa sia un modello Pydantic sia un mappatura di tabella ORM.
    #table=True specifica che si tratta di un modello relazionale, oltre che di un modello Pydantic -> Dice a SQLModel di generare anche la tabella corrispondente del database.
    username: str = Field(default=None, primary_key=True) #username è la chiave primaria
    name: str = Field()
    email: EmailStr = Field()