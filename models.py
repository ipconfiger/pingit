#coding=utf8
__author__ = 'alex'

import settings
import datetime
import uuid
from flask import g
from sqlalchemy import Column,Integer,String,DateTime,Boolean,Text,UniqueConstraint,Table, MetaData,ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship,backref
import utils
from decimal import Decimal
import json

TABLEARGS = {
    'mysql_engine': 'InnoDB',
    'mysql_charset':'utf8'
}

class DeclaredBase(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    id =  Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, default=datetime.datetime.now, index=True)
    last_modify = Column(DateTime, default=datetime.datetime.now, index=True)
    removed = Column(Boolean, default=False, index=True)

Base = declarative_base(cls=DeclaredBase)



class Resource(Base):
    ip_addr = Column(String(15))
    forward_id = Column(Integer)
    status = Column(Integer, default=0, index=True, doc="0:初始化1:正常2:有丢表3:全丢")
    comment = Column(Text)
    pingit = Column(Boolean)

    __table_args__ = (
        UniqueConstraint(ip_addr,),
        TABLEARGS
    )

    def __init__(self, ip, comment, forward_id = 0, allowed_ping = False):
        self.forward_id = forward_id
        self.ip_addr = ip
        self.comment =  comment
        self.pingit =  allowed_ping

    def change(self):
        if self.removed:
            self.removed = False
        else:
            self.removed = True

    @property
    def path(self):
        father = g.db.query(Resource).get(self.forward_id)
        if father:
            yield father
            father.path

    @property
    def next_ips(self):
        return g.db.query(Resource).filter(Resource.forward_id==self.id).order_by(Resource.id.asc())


class ErrorLog(Base):
    error_id = Column(String(32))
    resource_id = Column(Integer)
    comment = Column(Text)
    error = Column(Boolean)
    show = Column(Boolean)
    __table_args__ = (
        UniqueConstraint(error_id,),
        TABLEARGS
    )

    def __init__(self, error_id, resource_id):
        self.error_id = error_id
        self.resource_id = resource_id
        self.comment = "No Comment:add something"
        self.error = True
        self.show =True

    def update(self, comment, hide):
        self.comment = comment
        if hide:
            self.show = False
        g.db.flush()
        g.db.commit()

    @property
    def ip(self):
        return g.db.query(Resource).get(self.resource_id) or dict(ip_addr="deleted",comment="deleted",create_time=datetime.datetime.now())


class Config(Base):
    key = Column(String(40),unique=True)
    value = Column(String(500))

    def __init__(self, key, value):
        self.key = key
        self.value = json.dumps({"value":value})

    @property
    def data(self):
        return  json.loads(self.value)["value"]

    def set_value(self, value):
        self.value = json.dumps({"value":value})
