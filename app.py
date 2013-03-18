#coding=utf8
__author__ = 'alex'
import os
import logging
from flask import Flask, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flask.ext.script import Manager
import utils
import settings
import views
import biz

app = Flask(__name__)
app.config.from_object(settings)
manager = Manager(app)

app.register_blueprint(views.index)

cache = utils.Cache(*settings.REDIS_CNF)
DB=create_engine(settings.DB_URI,encoding = "utf-8",pool_recycle=settings.TIMEOUT,echo=False)
Session = scoped_session(sessionmaker(bind=DB))
cache.subscribe(['backworker'])

@app.before_request
def before_request():
    """
    在请求执行前执行
    """
    g.cache = cache
    g.db = Session()
    g.config = biz.ConfigDict(g.db)

@app.after_request
def after_request(response):
    try:
        g.db.flush()
        g.db.commit()
    except Exception, e:
        g.db.rollback(utils.print_debug(e))
    return response


@app.teardown_request
def tear_down(exception=None):
    """
    当请求结束的时候执行
    """
    try:
        if exception:
            g.db.rollback()
            g.db.close()
            logging.error(utils.print_debug(exception))
    except Exception, e:
        logging.error(utils.print_debug(e))


@manager.command
def init_db():
    g.db = Session()
    from models import Base
    Base.metadata.create_all(bind=DB)
    biz.init_config()
    print "done"

@manager.command
def monitor(execute_path):
    def on_message(channel,message):
        print channel, message
        logging.info("channel %s get message %s"%(channel, message))
        if message == "reboot":
            exit_code = os.system(execute_path)
            info = "command %s exit with %s"%(execute_path, exit_code)
            print info
            logging.info(info)

    g.cache = cache
    g.cache.listen(on_message)


if __name__ == "__main__":
    manager.run()