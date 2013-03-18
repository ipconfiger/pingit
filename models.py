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

class ResourceGroup(Base):
    group_id = Column(Integer)
    resource_id = Column(Integer)
    __table_args__ =(
        UniqueConstraint(group_id,resource_id,),
        TABLEARGS
    )
    def __init__(self, group, resource):
        self.group_id = group.id
        self.resource_id = resource.id

class Group(Base):
    group_id = Column(String(20), unique=True)
    comment = Column(Text)
    def __init__(self, ip, text):
        self.group_id = ip
        self.comment = text

    @property
    def IPs(self):
        for resourcegroup in g.db.query(ResourceGroup).filter(ResourceGroup.group_id==self.id):
            yield g.db.query(Resource).get(resourcegroup.resource_id)




class Resource(Base):
    ip_addr = Column(String(15))
    status = Column(Integer, default=0, index=True, doc="0:初始化1:正常2:有丢表3:全丢")
    comment = Column(Text)

    __table_args__ = (
        UniqueConstraint(ip_addr,),
        TABLEARGS
    )

    def __init__(self,ip,comment):
        self.ip_addr = ip
        self.comment =  comment

    @property
    def groups(self):
        for resourcegroup in g.db.query(ResourceGroup).filter(ResourceGroup.resource_id==self.id):
            yield g.db.query(Group).get(resourcegroup.group_id)

    def change(self):
        if self.removed:
            self.removed = False
        else:
            self.removed = True


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
