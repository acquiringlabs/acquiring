import os
import uuid
from datetime import datetime, timezone
from typing import Type

import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

from acquiring import domain, protocols

load_dotenv()  # take environment variables from .env.


SQLALCHEMY_DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")

engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URL)
session = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)()
Model: Type = declarative_base()  # TODO Remove Type hint (by using sqlalchemy stubs?)


def u() -> str:
    """Turn UUID to string for Identifiable to pass an uuid value to id"""
    return str(uuid.uuid4())


def now() -> datetime:
    return datetime.now(timezone.utc)


class Identifiable:
    """Mixin for models that can be identified"""

    # https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.Uuid
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True, default=u)

    # https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.TIMESTAMP
    created_at = sqlalchemy.Column(
        sqlalchemy.TIMESTAMP(timezone=True), default=now, server_onupdate=None, nullable=False
    )


class PaymentAttempt(Identifiable, Model):
    __tablename__ = "acquiring_paymentattempts"
    payment_methods = orm.relationship("PaymentMethod", back_populates="payment_attempt", cascade="all, delete")

    def to_domain(self) -> "protocols.PaymentAttempt":
        return domain.PaymentAttempt(
            id=self.id,
            created_at=self.created_at,
            amount=0,  # TODO Fill
            currency="FAKE",  # TODO Fill
            items=[],
            payment_methods=[payment_method.to_domain() for payment_method in self.payment_methods],
        )


class PaymentMethod(Identifiable, Model):
    __tablename__ = "acquiring_paymentmethods"

    confirmable = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, server_default="False")

    payment_attempt_id = sqlalchemy.Column(
        sqlalchemy.String, sqlalchemy.ForeignKey("acquiring_paymentattempts.id"), nullable=False
    )
    payment_attempt = orm.relationship("PaymentAttempt", back_populates="payment_methods", cascade="all, delete")

    operation_events = orm.relationship("OperationEvent", back_populates="payment_method", cascade="all, delete")
    block_events = orm.relationship("BlockEvent", back_populates="payment_method", cascade="all, delete")
    transactions = orm.relationship("Transaction", back_populates="payment_method", cascade="all, delete")

    def to_domain(self) -> "protocols.PaymentMethod":
        return domain.PaymentMethod(
            id=self.id,
            created_at=self.created_at,
            tokens=[],  # TODO Fill
            payment_attempt_id=self.payment_attempt_id,
            operation_events=[operation_event.to_domain() for operation_event in self.operation_events],
            confirmable=self.confirmable,
        )


class PaymentMilestone(Model):
    __tablename__ = "acquiring_paymentmilestones"

    # The high amount of instances expected for this model justifies the use of UUID instead of Integer
    # It is not identifiable, though, and the id doesn't get passed to the domain dataclass.
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True, default=u)

    created_at = sqlalchemy.Column(
        sqlalchemy.TIMESTAMP(timezone=True), default=now, server_onupdate=None, nullable=False
    )

    # Unlike Django, enum values are validated only at the domain layer
    # Reason: I've worked with enums on the database itself and they are nightmare.
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    payment_method_id = sqlalchemy.Column(
        sqlalchemy.String, sqlalchemy.ForeignKey("acquiring_paymentmethods.id"), nullable=False
    )
    payment_method = orm.relationship("PaymentMethod", cascade="all, delete")

    payment_attempt_id = sqlalchemy.Column(
        sqlalchemy.String, sqlalchemy.ForeignKey("acquiring_paymentattempts.id"), nullable=False
    )
    payment_attempt = orm.relationship("PaymentAttempt", cascade="all, delete")

    def __str__(self) -> str:
        return f"[type={self.type}, payment_attempt_id={self.payment_attempt_id}]"

    def to_domain(self) -> protocols.PaymentMilestone:
        return domain.PaymentMilestone(
            created_at=self.created_at,
            type=self.type,
            payment_attempt_id=self.payment_attempt_id,
            payment_method_id=self.payment_method.id,
        )


class OperationEvent(Model):
    __tablename__ = "acquiring_paymentoperations"

    # The high amount of instances expected for this model justifies the use of UUID instead of Integer
    # It is not identifiable, though, and the id doesn't get passed to the domain dataclass.
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True, default=u)

    created_at = sqlalchemy.Column(
        sqlalchemy.TIMESTAMP(timezone=True), default=now, server_onupdate=None, nullable=False
    )

    # Unlike Django, enum values are validated only at the domain layer
    # Reason: I've worked with enums on the database itself and they are nightmare.
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    payment_method_id = sqlalchemy.Column(
        sqlalchemy.String, sqlalchemy.ForeignKey("acquiring_paymentmethods.id"), nullable=False
    )
    payment_method = orm.relationship("PaymentMethod", back_populates="operation_events", cascade="all, delete")

    __table_args__ = (sqlalchemy.Index("ix_acquiring_paymentoperations_status", "status"),)

    def __str__(self) -> str:
        return f"[type={self.type}, status={self.status}]"

    def to_domain(self) -> "protocols.OperationEvent":
        return domain.OperationEvent(
            type=self.type,
            status=self.status,
            payment_method_id=self.payment_method_id,
            created_at=self.created_at,
        )


class BlockEvent(Model):
    __tablename__ = "acquiring_blockevents"

    # The high amount of instances expected for this model justifies the use of UUID instead of Integer
    # It is not identifiable, though, and the id doesn't get passed to the domain dataclass.
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True, default=u)

    created_at = sqlalchemy.Column(
        sqlalchemy.TIMESTAMP(timezone=True), default=now, server_onupdate=None, nullable=False
    )

    # Unlike Django, enum values are validated only at the domain layer
    # Reason: I've worked with enums on the database itself and they are nightmare.
    status = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    block_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    payment_method_id = sqlalchemy.Column(
        sqlalchemy.String, sqlalchemy.ForeignKey("acquiring_paymentmethods.id"), nullable=False
    )
    payment_method = orm.relationship("PaymentMethod", back_populates="block_events", cascade="all, delete")

    __table_args__ = (sqlalchemy.Index("ix_acquiring_blockevents_status", "status"),)

    def __str__(self) -> str:
        return f"[{self.block_name}|status={self.status}]"

    def to_domain(self) -> "protocols.BlockEvent":
        return domain.BlockEvent(
            status=self.status,
            payment_method_id=self.payment_method_id,
            block_name=self.block_name,
            created_at=self.created_at,
        )


class Transaction(Model):
    __tablename__ = "acquiring_transactions"

    # The high amount of instances expected for this model justifies the use of UUID instead of Integer
    # It is not identifiable, though, and the id doesn't get passed to the domain dataclass.
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True, default=u)

    external_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    timestamp = sqlalchemy.Column(
        sqlalchemy.TIMESTAMP(timezone=True), default=now, server_onupdate=None, nullable=False
    )

    raw_data = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    provider_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    payment_method_id = sqlalchemy.Column(
        sqlalchemy.String, sqlalchemy.ForeignKey("acquiring_paymentmethods.id"), nullable=False
    )
    payment_method = orm.relationship("PaymentMethod", back_populates="transactions", cascade="all, delete")

    def __str__(self) -> str:
        return f"[provider={self.provider_name}|payment_method={self.payment_method_id}|{self.external_id}]"

    def to_domain(self) -> "protocols.Transaction":
        return domain.Transaction(
            external_id=self.external_id,
            timestamp=self.timestamp,
            raw_data=self.raw_data,
            provider_name=self.provider_name,
            payment_method_id=self.payment_method_id,
        )
