from sqlalchemy.orm.session import Session as DbSession
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Unicode

from azafea.model import Base


class Event(Base):
    __tablename__ = 'managedb_event'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)


def process(dbsession: DbSession, record: bytes) -> None:
    pass
