
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column, text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from typing import Optional

class KBArticle(SQLModel, table=True):
    __tablename__ = "kb_article"
    id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    business_id: Optional[int] = Field(default=None, foreign_key="business.id")
    title: str | None = Field(default=None)
    content: dict = Field(sa_column=Column(JSONB))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("now()")}
    )
