#coding=utf8
__author__ = 'alex'

import gevent
from gevent import monkey
monkey.patch_all()
import ping
import utils

cache = utils.Cache("127.0.0.1",8)

def worker(idx, ip):
    while(True):
        node = cache.get("ip_%s"%idx)
        take_time = ping.do_one(ip,1,64)
        print ip, take_time
        if take_time:
            node["last_take"] = take_time
            node["live"] = True
        else:
            node["last_take"] = None
            node["live"] = False
        cache.set("ip_%s"%idx,node)
        gevent.sleep(seconds=60)

def main():
    nodes = []
    count_item = cache.get("count")
    if count_item:
        count = count_item["v"]
    else:
        count = 0
    for i in range(count):
        node = cache.get("ip_%s"%i)
        nodes.append(node)
    print nodes
    jobs = [gevent.spawn(worker, idx, node["ip"]) for idx,node in enumerate(nodes)]
    gevent.joinall(jobs)

if __name__ == "__main__":
    main()

