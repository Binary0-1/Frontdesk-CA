from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column, Integer, text
from sqlalchemy import DateTime
from typing import Optional


class Customer(SQLModel, table=True):
    __tablename__ = "customers"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            primary_key=True,
            autoincrement=True
        ),
    )

    name: Optional[str] = None
    phone: Optional[str] = None

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()")
        )
    )
