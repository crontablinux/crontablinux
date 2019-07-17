import os

class Config:
    SECRET_KEY = 'v3c$63l=r0cnt=p=n-1s0_1!%$c)251^dc=oq#ng#!*0c38+re'

    REDIS_HOST = os.environ.get('REDIS_HOST') or "127.0.0.1"
    REDIS_PORT = os.environ.get('REDIS_PORT') or 6379
    REDIS_PWD = os.environ.get('REDIS_PWD') or ""

    DB_ENGINE = "mysql"
    DB_NAME = os.environ.get('DB_NAME') or "crontablinux"
    DB_HOST = os.environ.get('DB_HOST') or "127.0.0.1"
    DB_PORT = os.environ.get('DB_PORT') or "3306"
    DB_USER = os.environ.get('DB_USER') or "root"
    DB_PASSWORD =  os.environ.get('DB_PASSWORD') or "root"

    HTTP_BIND_HOST = os.environ.get('HTTP_BIND_HOST') or '0.0.0.0'
    HTTP_LISTEN_PORT = os.environ.get('HTTP_LISTEN_PORT') or 8080

    LOG_LEVEL = 'INFO'
    DEBUG = False
