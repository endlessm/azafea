# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import pytest

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Text

from azafea.config import Config
import azafea.model


def test_use_db_session(monkeypatch, mock_sessionmaker):
    config = Config()

    with monkeypatch.context() as m:
        m.setattr(azafea.model, 'sessionmaker', mock_sessionmaker)
        db = azafea.model.Db(config.postgresql)

        with db as dbsession:
            assert dbsession.open
            assert not dbsession.committed
            assert not dbsession.rolled_back

        assert not dbsession.open
        assert dbsession.committed
        assert not dbsession.rolled_back


def test_fail_committing_db_session(monkeypatch, mock_sessionmaker):
    config = Config()

    def raise_when_committing():
        raise ValueError('Could not commit')

    with monkeypatch.context() as m:
        m.setattr(azafea.model, 'sessionmaker', mock_sessionmaker)
        db = azafea.model.Db(config.postgresql)

        with pytest.raises(ValueError) as exc_info:
            with db as dbsession:
                dbsession.commit = raise_when_committing

        assert 'Could not commit' in str(exc_info.value)

        assert not dbsession.open
        assert not dbsession.committed
        assert dbsession.rolled_back


def test_exit_from_already_rolled_back_session(monkeypatch, mock_sessionmaker):
    config = Config()

    with monkeypatch.context() as m:
        m.setattr(azafea.model, 'sessionmaker', mock_sessionmaker)
        db = azafea.model.Db(config.postgresql)

        with db as dbsession:
            assert dbsession.open
            assert not dbsession.committed
            assert not dbsession.rolled_back
            assert dbsession.is_active

            # We tried to commit something explicitly before exiting the context manager, an error
            # occured which rolled back the transaction; it is now inactive
            dbsession.rollback()

        assert not dbsession.open
        assert not dbsession.committed
        assert dbsession.rolled_back


def test_fail_in_db_session(monkeypatch, mock_sessionmaker):
    config = Config()

    with monkeypatch.context() as m:
        m.setattr(azafea.model, 'sessionmaker', mock_sessionmaker)
        db = azafea.model.Db(config.postgresql)

        with pytest.raises(ValueError) as exc_info:
            with db as dbsession:
                raise ValueError('Oh no!')

        assert 'Oh no!' in str(exc_info.value)

        assert not dbsession.open
        assert not dbsession.committed
        assert dbsession.rolled_back


def test_base_model():
    class Address(azafea.model.Base):
        __tablename__ = 'addresses'

        id = Column(Integer, primary_key=True)
        street_number = Column(Text)
        street_name = Column(Text)
        city = Column(Text)

    class Person(azafea.model.Base):
        __tablename__ = 'people'

        id = Column(Integer, primary_key=True)
        name = Column(Text)
        address_id = Column(Integer, ForeignKey('addresses.id'))

        address = relationship(Address)

    address = Address(id=1, street_number='221B', street_name='Baker Street', city='London',
                      # Extra arg, to ensure it is ignored
                      ignored='whatever')
    person = Person(id=1, name='Sherlock Holmes', address=address)

    assert str(person) == '\n'.join([
        '# azafea.tests.test_model.Person',
        '* address: 1',
        '* id: 1',
        '* name: Sherlock Holmes',
    ])
    assert str(address) == '\n'.join([
        '# azafea.tests.test_model.Address',
        '* city: London',
        '* id: 1',
        '* street_name: Baker Street',
        '* street_number: 221B',
    ])

    # Deregister the test models, to avoid side-effects between tests
    azafea.model.Base.registry.dispose()
    azafea.model.Base.metadata.clear()
    azafea.model.Base.metadata.dispatch._clear()
