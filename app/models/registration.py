from sqlmodel import SQLModel, Field #la classe SQLModel per i modelli ORM/Pydantic, Field per applicare dei vincoli sui dati



class Registration(SQLModel, table=True): #modello relazionale, genera una tabella nel database che mette in relazione Event e User
    username: str = Field(primary_key=True, foreign_key="user.username") #Definisce un campo username che è una chiave esterna
    event_id: int = Field(primary_key=True, foreign_key="event.id") #Definisce un campo event_id che è una chiave esterna
