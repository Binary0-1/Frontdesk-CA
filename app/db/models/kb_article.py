from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column, Integer, text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from typing import Optional


class KBArticle(SQLModel, table=True):
    __tablename__ = "kb_article"

    id: uuid.UUID = Field(
        default=None,
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )

    business_id: int = Field(
        foreign_key="business.id",
        nullable=False
    )

    title: Optional[str] = None

    content: dict = Field(
        sa_column=Column(JSONB, nullable=False)
    )

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),   
            nullable=False,
            server_default=text("now()")
        )
    )
