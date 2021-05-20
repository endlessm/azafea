# Copyright (c) 2019 - Endless
#
# This file is part of Azafea
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, Integer, Unicode

from azafea.model import Base


class Channel(Base):
    __tablename__ = 'channel_v3'

    id = Column(Integer, primary_key=True)

    #: image ID (e.g. ``eos-eos3.1-amd64-amd64.170115-071322.base``)
    image_id = Column(Unicode, nullable=False)
    #: dictionary of string keys (such as ``facility``, ``city`` and
    #: ``state``) to the values provided in the location.conf file (written by
    #: the ``eos-label-location`` utility)
    site = Column(JSONB, nullable=False)
    #: dual boot computer
    dual_boot = Column(Boolean, nullable=False)
    #: live USB stick
    live_usb = Column(Boolean, nullable=False)
