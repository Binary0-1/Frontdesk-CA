from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Integer, text
from sqlalchemy import DateTime
from datetime import datetime
from typing import Optional


class Business(SQLModel, table=True):
    __tablename__ = "business"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            primary_key=True,
            autoincrement=True
        )
    )

    name: str = Field(nullable=False)

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()")
        )
    )
