#coding=utf8
__author__ = 'alex'
import logging
from flask import g
from IPy import IP
from utils import *
from models import *

def valid_ip(ip):
    return int(ip.split(".")[3]) not in [0,255]


def add_ip(addr, comment, forward_id):
    ips = [str(ip) for ip in IP(addr) if valid_ip(str(ip))]
    for ip in ips:
        g.db.add(Resource(ip,comment,forward_id=forward_id, allowed_ping=True))
    g.db.flush()
    g.db.commit()


def get_res(res):
    for r in res.next_ips:
        get_res(r)
        g.db.delete(r)

def delete_ip(ipid):
    resource = g.db.query(Resource).get(ipid)
    for res in resource.next_ips:
        get_res(res)
        g.db.delete(res)
    g.db.delete(resource)
    g.db.flush()
    g.db.commit()




def current_alerts():
    return g.db.query(ErrorLog).filter(ErrorLog.error==True).order_by(ErrorLog.id.desc())

def normal_log():
    return g.db.query(ErrorLog).filter(ErrorLog.error==False,ErrorLog.show==True).order_by(ErrorLog.id.desc())


class ConfigDict(object):
    def __init__(self, db):
        self.db = db
        self.data = {}
        try:
            for cfg in db.query(Config).all():
                self.data[cfg.key] = cfg
        except Exception, e:
            pass

    def __getitem__(self, item):
        return self.data[item].data

    def __setitem__(self, key, value):
        if key in self.data:
            self.data[key].set_value(value)
        else:
            cfg = Config(key, value)
            self.db.add(cfg)
            self.db.flush()
            self.data[key] = cfg


def init_config():
    config = ConfigDict(g.db)
    config["wait"] = 60
    config["time_out"] = 1
    config["ping_times"] = 4
    config["site_title"] = "Sagittarius"
    config["copyright"] = "@from alexander 2013"
    g.db.flush()
    g.db.commit()