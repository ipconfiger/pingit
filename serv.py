#coding=utf8
__author__ = 'alex'

import gevent
from gevent import monkey
monkey.patch_all()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import ping
import settings
from models import Resource
from biz import  ConfigDict

DB=create_engine(settings.DB_URI,encoding = "utf-8",pool_recycle=settings.TIMEOUT,echo=False)
Session = scoped_session(sessionmaker(bind=DB))
db = Session()
config = ConfigDict(db)

def worker(node_id,ip_addr):
    last_level = -1
    while(True):
        level = 0
        for i in range(int(config["ping_times"])):
            try:
                take_time = ping.do_one(ip_addr,int(config["time_out"]),64)
                print "ping", ip_addr, take_time
            except Exception, e:
                take_time = None
            if take_time:
                level+=1
        if level!=last_level:
            db.commit()
            node = db.query(Resource).get(node_id)
            if not node:
                break
            if level==int(config["ping_times"]):
                node.status = 1
            if 0<level<int(config["ping_times"]):
                node.status = 2
            if not level:
                node.status = 3
            db.flush()
            db.commit()
            last_level = level
        gevent.sleep(seconds=int(config["wait"]))

def main():
    nodes = list(db.query(Resource).filter(Resource.removed==False).all())
    print "get %s ips"%len(nodes)
    jobs = [gevent.spawn(worker, node.id, node.ip_addr) for node in nodes]
    gevent.joinall(jobs)

if __name__ == "__main__":
    main()

