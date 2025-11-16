
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import text, Column
from typing import Optional

class Business(SQLModel, table=True):
    __tablename__ = "business"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("now()")}
    )
