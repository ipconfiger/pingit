#coding=utf8
__author__ = 'alex'

import logging
from tempfile import NamedTemporaryFile
from flask import Blueprint, render_template, abort, g, request, redirect, url_for, session, flash, send_file
from utils import *

index = Blueprint('index', __name__,template_folder='templates',url_prefix='/')

@index.route("")
def index_page():
    return render_template("index.html",**locals())