#coding=utf8
__author__ = 'alex'

import logging
from tempfile import NamedTemporaryFile
from flask import Blueprint, render_template, abort, g, request, redirect, url_for, session, flash, jsonify
from utils import *
from biz import *

index = Blueprint('index', __name__,template_folder='templates',url_prefix='')

@index.app_template_filter(name="dateTime")
def format_date(dt):
    return "%s-%s-%s %s:%s:%s"%(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)


@index.route("/")
def index_page():
    return render_template("index.html",**locals())

@index.route("/watch",methods=["POST"])
def change():
    alerts = current_alerts()
    logs = normal_log()
    return render_template("_groups.html",**locals())


@index.route("/ip",methods=["POST"])
def add_new_ip():
    try:
        ip_addr = request.form.get("addr")
        comment = request.form.get("comment")
        forward_id = int(request.form.get("forward"))
        add_ip(ip_addr, comment, forward_id)
        return jsonify(rs=True,info=u"successfull")
    except Exception, e:
        logging.error(print_debug(e))
        return jsonify(rs=False,info=u"Unkown Error!")

@index.route("/manage/<father_id>")
def config_ip_view(father_id):
    father_id = int(father_id)
    if father_id:
        node = g.db.query(Resource).get(father_id)
        top_level = list(node.next_ips)
    else:
        node = None
        top_level = list(g.db.query(Resource).filter(Resource.forward_id==0).order_by(Resource.id.asc()))

    return render_template("config_ips.html",**locals())


@index.route("/manage/ip/comment", methods=["POST"])
def update_comment():
    try:
        resource = g.db.query(Resource).get(request.form.get("rcid"))
        resource.comment = request.form.get("comment")
        g.db.flush()
        g.db.commit()
        return jsonify(rs=True,info="")
    except Exception, e:
        g.db.rollback()
        return jsonify(rs=False,info=u"未知异常")

@index.route("/manage/ip/ping/status", methods=["POST"])
def ping_status():
    try:
        resource = g.db.query(Resource).get(request.form.get("rcid"))
        if resource.pingit:
            resource.pingit = False
        else:
            resource.pingit = True
        g.db.flush()
        g.db.commit()
        return jsonify(rs=True,info="")
    except Exception, e:
        g.db.rollback()
        return jsonify(rs=False,info=u"未知异常")

@index.route("/manage/ip/delete", methods=["POST"])
def delete_resource():
    try:
        delete_ip(int(request.form.get("rcid")))
        return jsonify(rs=True,info="")
    except Exception, e:
        g.db.rollback()
        return jsonify(rs=False,info=u"未知异常")



@index.route("/manage/ip/log", methods=["POST"])
def append_log():
    try:
        error_id = request.form.get("error_id")
        hide = True if int(request.form.get("hide")) else False
        comment = request.form.get("comment")
        errorlog = g.db.query(ErrorLog).get(error_id)
        if errorlog:
            errorlog.update(comment,hide)
            return jsonify(rs=True,info="")
        return jsonify(rs=False,info=u"Not Exist")
    except Exception,e:
        g.db.rollback()
        logging.error(print_debug(e))
        return jsonify(rs=False, info=u"未知异常")




@index.route("/manage/ip/delete", methods=["POST"])
def reousce_delete():
    try:
        resource = g.db.query(Resource).get(request.form.get("rcid"))
        resource.change()
        g.db.flush()
        g.db.commit()
        return jsonify(rs=True,info="")
    except Exception, e:
        g.db.rollback()
        return jsonify(rs=False,info=u"未知异常")

@index.route("/manage/log")
def error_logs(page_size=20):
    pid = int(request.form.get("p","1"))
    q = g.db.query(ErrorLog).order_by(ErrorLog.id.desc())
    total = q.count()
    pids = pages(total, page_size)
    logs = q[(pid-1)*page_size:pid*page_size]
    return render_template("error_logs.html",**locals())


@index.route("/manage/config", methods=["POST"])
def update_config():
    try:
        key = request.form.get("key")
        v = request.form.get("v")
        g.config[key] = v
        g.db.commit()
        return jsonify(rs=True)
    except Exception, e:
        g.db.rollback()
        return jsonify(rs=False)

@index.route("/manage/apply",methods=["POST"])
def apply_changes():
    g.cache.publish("backworker","refresh")
    return jsonify(rs=True)