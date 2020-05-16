import os
import time
import logging
import threading
from functools import wraps

import sqlalchemy as sa

from db import init_db
from ping import ping
from app import create_app

ENVIRONMENT = os.environ.get("FLASK_ENV", "development")
PING_HOSTS = os.environ.get("PING_HOSTS", "google.com")
PING_DELAY_SEC = int(os.environ.get("PING_DELAY_SEC", 60))
DB_URL = os.environ.get("DB_URL")

DEBUG = ENVIRONMENT == "development"

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(lineno)-4s <%(funcName)s> - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)
logger.info("Starting ping %s in %s environment", PING_HOSTS, ENVIRONMENT)

assert DB_URL, "No DB_URL..."
assert PING_HOSTS, "Empty host..."

engine = sa.create_engine(DB_URL)
db = init_db(engine)


def run_as_thread(fn):
    """Run function as thread"""

    @wraps(fn)
    def run(*args, **kwargs):
        t = threading.Thread(target=fn, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
        return t

    return run


@run_as_thread
def log_ping(host, ts):
    res = ping(host)
    logger.debug("%s: %s", res.host, res.time_ms)
    with db.session():
        db.Ping.create(res.host, res.time_ms, ts)


@run_as_thread
def ping_tester(hosts):
    while True:
        ts = int(time.time())
        for host in hosts:
            log_ping(host, ts)
        time.sleep(PING_DELAY_SEC)


if __name__ == "__main__":
    ping_tester(tuple({h for h in PING_HOSTS.split(",")}))

    app = create_app()
    app.run(host="0.0.0.0")
