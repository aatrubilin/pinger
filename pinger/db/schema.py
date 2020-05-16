import logging
from datetime import datetime

import sqlalchemy as sa

from .base import Base, Session

__all__ = ["Ping"]

logger = logging.getLogger(__name__)


class Ping(Base):
    __tablename__ = 'pings'

    id = sa.Column(sa.Integer, primary_key=True)
    host = sa.Column(sa.String, nullable=False)
    ping = sa.Column(sa.Float, nullable=True)
    ts = sa.Column(sa.Integer, nullable=False)

    query = Session.query_property()

    def __init__(self, host, ping, ts):
        self.host = host
        self.ping = ping
        self.ts = ts

    def __repr__(self):
        return "<Ping({s.id!r}, {s.host!r}, {s.ping})>".format(s=self)

    @classmethod
    def create(cls, host, ping, ts):
        ping = cls(host, ping, ts)
        Session.add(ping)
        Session.flush()
        logger.debug("Created %r", ping)
        return ping
