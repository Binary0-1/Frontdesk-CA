
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import text, Column
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Business(SQLModel, table=True):
    __tablename__ = "business"
    id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    name: str = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("now()")}
    )
