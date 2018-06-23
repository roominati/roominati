from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, composite
from sqlalchemy import Column, Time, DateTime, Integer, Boolean, String
from sqlalchemy import Interval, ForeignKey
from sqlalchemy.types import TypeDecorator
import sqlalchemy.types as types
from dateutil.tz import UTC


class Moment(TypeDecorator):
    impl = types.DateTime()

    def __init__(self, *args, **kwargs):
        kwargs.pop("timezone", None)  # We want `timezone` to be True
        super().__init__(*args, timezone=True, *kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        assert value.tzinfo is not None
        return value.astimezone(UTC)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return value.replace(tzinfo=UTC)

    def copy(self, **kw):
        return Moment(self.impl.timezone)


class Lapse(object):
    def __init__(self, start_at, duration):
        self.start_at = start_at
        self.duration = duration

    def __composite_values__(self):
        return self.start_at, self.duration

    def __repr__(self):
        return f"Lapse(start_at={self.start_at}, duration={self.duration})"

    def __eq__(self, other):
        return isinstance(other, Lapse) and \
               other.start_at == self.start_at and \
               other.duration == self.duration

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def end_at(self):
        return self.start_at + self.duration

    def contains(self, inner):
        return self.start_at <= inner.start_at and inner.end_at <= self.end_at

    def precedes(self, other: datetime):
        return self.start_at < other

    def increment(self):
        self.start_at += self.duration


Base = declarative_base()


class Host(Base):
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True)
    token = Column(String)
    breakouts = relationship("Breakout", back_populates="host")


class Breakout(Base):
    __tablename__ = "breakouts"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    start_at = Column(Moment)
    duration = Column(Interval)
    lapse = composite(Lapse, start_at, duration)
    posted = Column(Boolean)
    posted_at = Column(Moment)
    host_id = Column(Integer, ForeignKey("hosts.id"))
    host = relationship("Host", back_populates="breakouts")
