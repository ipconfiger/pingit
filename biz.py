#coding=utf8
__author__ = 'alex'
import logging
from flask import g
from IPy import IP
from utils import *
from models import *

def valid_ip(ip):
    return int(ip.split(".")[3]) not in [0,255]

def _save_group(addr,ips,comment):
    if len(ips)<2:
        addr = ".".join(addr.split(".")[:3]+["0"])+"/24"
    if g.db.query(Group).filter(Group.group_id==addr).count()<1:
        group = Group(addr,comment)
        g.db.add(group)
        g.db.flush()
    else:
        group = g.db.query(Group).filter(Group.group_id==addr).one()
    return group

def _save_relation(group,resource):
    if g.db.query(ResourceGroup).filter(ResourceGroup.group_id==group.id,ResourceGroup.resource_id==resource.id).count()<1:
        resourcegroup = ResourceGroup(group,resource)
        g.db.add(resourcegroup)
        g.db.flush()

def add_ip(addr, comment):
    ips = [str(ip) for ip in IP(addr) if valid_ip(str(ip))]
    group = _save_group(addr, ips, comment)
    for ip in ips:
        if g.db.query(Resource).filter(Resource.ip_addr==ip).count()<1:
            resource = Resource(ip,comment)
            g.db.add(resource)
            g.db.flush()
        else:
            resource = g.db.query(Resource).filter(Resource.ip_addr==ip).one()
        _save_relation(group, resource)
    g.db.commit()

def get_groups():
    return list(g.db.query(Group).filter(Group.removed==False).all())

def get_group(group_id):
    return g.db.query(Group).get(group_id)

def get_resources(group_id):
    for resourcegroup in g.db.query(ResourceGroup).filter(ResourceGroup.group_id==group_id):
        yield g.db.query(Resource).get(resourcegroup.resource_id)

def get_alerts():
    group_alert = {}
    for resource in g.db.query(Resource).filter(Resource.status>1):
        for group in resource.groups:
            if group.id in group_alert:
                group_alert[group.id].append(resource)
            else:
                group_alert[group.id] = [resource,]
    return group_alert

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