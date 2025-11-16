import enum
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column, Integer, Enum, DateTime, text
from typing import Optional


class HelpStatus(enum.Enum):
    pending = "pending"
    resolved = "resolved"
    timed_out = "timed_out"


class HelpRequest(SQLModel, table=True):
    __tablename__ = "help_requests"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            primary_key=True,
            autoincrement=True
        )
    )

    customer_id: int = Field(
        foreign_key="customers.id",
        nullable=False
    )

    business_id: int = Field(
        foreign_key="business.id",
        nullable=False
    )

    question: str = Field(nullable=False)

    status: HelpStatus = Field(
        default=HelpStatus.pending,
        sa_column=Column(
            Enum(HelpStatus, name="helpstatus"),
            nullable=False,
            server_default=text("'pending'")
        )
    )

    supervisor_answer: Optional[str] = None

    answered_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True
        )
    )

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()")
        )
    )
