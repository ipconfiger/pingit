#coding=utf8
__author__ = 'alex'
import sys
import os
import logging
import redis
from flask import Flask, g, session, request, render_template
import settings
from flask.ext.script import Manager
from utils import *

app = Flask("yun")
app.config.from_object(settings)
manager = Manager(app)

cache = Cache('127.0.0.1',8)

@app.route("/")
def index():
    return render_template("index.html",**locals())

@manager.command
def init(ip):
    count_item = cache.get("count")
    if count_item:
        count = count_item["v"]
    else:
        count = 0
    cache.set("ip_%s"%count,{"ip":ip,"last_take":None,"live":True})
    cache.set("count",{"v":count+1})
    print "add %s ok"%ip

@manager.command
def serv():
    pass