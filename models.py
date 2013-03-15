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
    removed = Column(Boolean, default=False)

Base = declarative_base(cls=DeclaredBase)


class Resource(Base):
    title = Column(String(50))
    ip_addr = Column(String(15))
    status = Column(Integer, default=0, doc="0:初始化1:正常2:有丢表3:全丢")
    comment = Column(Text)

    __table_args__ = (
        UniqueConstraint(ip_addr,),
        TABLEARGS
    )

    def __init__(self,ip,title,comment):
        self.title = title
        self.ip_addr = ip
        self.comment =  comment


