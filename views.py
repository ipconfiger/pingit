#coding=utf8
__author__ = 'alex'

import logging
from tempfile import NamedTemporaryFile
from flask import Blueprint, render_template, abort, g, request, redirect, url_for, session, flash, jsonify
from utils import *
from biz import *

index = Blueprint('index', __name__,template_folder='templates',url_prefix='')

@index.route("/")
def index_page():
    return render_template("index.html",**locals())

@index.route("/watch",methods=["POST"])
def change():
    groups = get_groups()
    alerts = get_alerts()
    return render_template("_groups.html",**locals())


@index.route("/ip",methods=["POST"])
def add_new_ip():
    try:
        ip_addr = request.form.get("addr")
        comment = request.form.get("comment")
        add_ip(ip_addr, comment)
        return jsonify(rs=True,info=u"successfull")
    except Exception, e:
        logging.error(print_debug(e))
        return jsonify(rs=False,info=u"Unkown Error!")

@index.route("/manage")
def config_ip_view():
    groups = get_groups()
    return render_template("config_ips.html",**locals())

@index.route("/manage/ip", methods=["POST"])
def load_ips():
    group_id = request.form.get("rcid")
    group = get_group(group_id)
    items = get_resources(group_id)
    return render_template("_item.html",**locals())

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

@index.route("/manage/group/comment", methods=["POST"])
def update_group():
    try:
        group_id = request.form.get("gid")
        comment = request.form.get("comment")
        group = get_group(group_id)
        group.comment = comment
        g.db.rollback()
        return jsonify(rs=True)
    except Exception, e:
        g.db.rollback()
        print_debug(e)
        return jsonify(rs=False)


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
    g.cache.publish("backworker","reboot")
    return jsonify(rs=True)