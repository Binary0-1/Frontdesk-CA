from sqlmodel import SQLModel, create_engine, Session
from config import settings
from .models.customer import Customer
from .models.help_request import HelpRequest
from .models.supervisor import Supervisor
from .models.knowledge_base import KnowledgeBase

engine = create_engine(settings.DB_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
