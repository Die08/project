from pydantic import EmailStr #per accettare stringhe con un formato email valido
from sqlmodel import SQLModel, Field #la classe SQLModel per i modelli ORM/Pydantic, Field per applicare dei vincoli sui dati

class UserBase(SQLModel): #Definizione della classe UserBase.
    username: str = Field(default=None, primary_key=True) #username è la chiave primaria
    name: str = Field()
    email: EmailStr = Field()

class User(UserBase, table=True): #Definizione della classe User
    #table=True specifica che si tratta di un modello relazionale
    pass

class UserCreate(UserBase):
    pass
