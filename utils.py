#coding=utf8
__author__ = 'alex'
import redis
import json

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
