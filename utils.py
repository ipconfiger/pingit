#coding=utf8
__author__ = 'alex'
import sys
import redis
import json
import traceback


def tob(s, enc='utf8'):
    return s.encode(enc) if isinstance(s, unicode) else bytes(s)
def touni(s, enc='utf8', err='strict'):
    return s.decode(enc, err) if isinstance(s, bytes) else unicode(s)


class Cache(object):
    def __init__(self,host,db):
        self.redis = redis.Redis(host=host,port=6379,db=db)

    def _gen_key(self,key,pub=False):
        return "publish_%s"%key if pub else "object_%s"%key

    def get(self, name, loads = json.loads):
        data = self.redis.get(self._gen_key(name))
        if data:
            return loads(data)

    def set(self, name, value, ttl=3600, dumps = json.dumps):
        if ttl:
            return self.redis.setex(self._gen_key(name), dumps(value), ttl)
        return self.redis.set(self._gen_key(name), dumps(value))

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        return self.set(key,value,ttl=0)

    def delete(self, key):
        self.redis.delete(self._gen_key(key))


    def subscribe(self, channels):
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)

    def publish(self, channel, message):
        self.redis.publish(channel, json.dumps(message))

    def listen(self, on_message):
        for message in self.pubsub.listen():
            if message.get("type") == "message":
                on_message(message.get("channel"), json.loads(message.get("data")))

class Frame(object):
    def __init__(self, tb):
        self.tb = tb
        frame = tb.tb_frame
        self.locals = {}
        self.locals.update(frame.f_locals)

    def print_path(self):
        return touni(traceback.format_tb(self.tb, limit=1)[0])

    def print_local(self):
        return u"\n".join(["%s=%s" % (k, self.dump_value(self.locals[k])) for k in self.locals])

    def dump_value(self, v):
        try:
            return touni(str(v))
        except:
            return u"value can not serilizable"

def print_debug(ex):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    frames = []
    tb = exc_traceback
    frames.append(tb.tb_frame)
    detail = u"alex error -Exception:%s\n" % ex
    while tb.tb_next:
        tb = tb.tb_next
        fm = Frame(tb)
        detail += fm.print_path()
        detail += u"\nlocals variables:\n"
        detail += fm.print_local()
        detail += u"\n-------------------------------------------------------\n"
    return detail
