from sqlmodel import SQLModel, create_engine, Session
from config import settings
from .models.business import Business
from .models.help_request import HelpRequest
from .models.kb_article import KBArticle
from .models.supervisor_response import SupervisorResponse

engine = create_engine(settings.DB_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
