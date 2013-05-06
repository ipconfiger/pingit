#coding=utf8
__author__ = 'alex'

import uuid
import gevent
from gevent import monkey
monkey.patch_all()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import ping
import logging
import settings
from models import Resource, ErrorLog
from biz import  ConfigDict
import Queue
import utils

if not settings.LOCAL:
    db_url = settings.DB_URI.replace("mysql:","mysql+mysqlconnector:")
else:
    db_url = settings.DB_URI
DB=create_engine(db_url,encoding = "utf-8",pool_recycle=settings.TIMEOUT,echo=False)
Session = scoped_session(sessionmaker(bind=DB))
db = Session()
config = ConfigDict(db)
Q = Queue.Queue()
WORKERS = []

def db_work(node_id, status, error_id):
    db.commit()
    resource = db.query(Resource).get(node_id)
    if not resource:
        return
    resource.status = 1 if status else 3
    if status:
        try:
            errorlog = db.query(ErrorLog).filter(ErrorLog.error_id == error_id).one()
            errorlog.error = False
        except:
            pass
    else:
        try:
            errorlog = db.query(ErrorLog).filter(ErrorLog.error_id == error_id).one()
            errorlog.error = True
        except:
            errorlog = ErrorLog(error_id, resource.id)
            db.add(errorlog)
    db.flush()
    db.commit()


def dumper():
    while True:
        if Q.empty():
            gevent.sleep(0.5)
            continue
        db_work(*Q.get())


def ping(ip_addr):
    try:
        take_time = ping.do_one(ip_addr,int(config["time_out"]),64)
    except Exception, e:
        take_time = None
    return True if take_time else False

def worker(node_id,ip_addr):
    ping_ok = True
    current_status = ping_ok
    last_status = ping_ok
    last_error_id = None
    while(True):
        if reduce(lambda a,b: a and b,[ping(ip_addr) for i in xrange(int(config["ping_times"]))]):
              if last_status != ping_ok:
                  #上次如果是失败的话就重置状态为成功
                  Q.put((node_id, True, last_error_id))
                  last_status = ping_ok
                  last_error_id = None
        else:
            if last_status == ping_ok:
                #如果上次是成功的话就重置状态为失败，如果已经是失败状态就不重复操作
                last_error_id = uuid.uuid4().hex
                Q.put((node_id, False, last_error_id))
                last_status = False
        gevent.sleep(seconds=int(config["wait"]))


def update_workers():
    global WORKERS
    if WORKERS:
        gevent.killall(WORKERS)
    del WORKERS[:]
    nodes = list(db.query(Resource).filter(Resource.removed==False).all())
    logging.error(nodes)
    for job in [gevent.spawn(worker, node.id, node.ip_addr) for node in nodes]:
        WORKERS.append(job)
    gevent.joinall(WORKERS)


def monitor():
    def on_message(chn, message):
        if chn=='backworker' and message=='refresh':
            gevent.spawn(update_workers).start()

    cache = utils.Cache(*settings.REDIS_CNF)
    cache.subscribe(['backworker'])
    cache.listen(on_message)

def main():
    gevent.joinall([gevent.spawn(monitor),gevent.spawn(dumper),gevent.spawn(update_workers)])

if __name__ == "__main__":
    main()

