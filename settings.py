#coding=utf8
__author__ = 'alex'
import os

DEBUG = True
LOCAL = True
if LOCAL:
    DB_URI = "mysql://root:123456@127.0.0.1:3306/ping?charset=utf8"
else:
    DB_URI = "mysql://root:zzf12345@127.0.0.1:3306/ping?charset=utf8"

TIMEOUT = 3600*6

SECRET_KEY = "11556653333221changge!"

SELF_KEY = 'edhwr8~w'

REDIS_CNF = ("127.0.0.1",8)

MEDIA_ROOT = "/static"

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
UPFILE_ROOT = os.path.abspath(os.path.join(SITE_ROOT, 'static','upload'))
