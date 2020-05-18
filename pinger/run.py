import os
import time
import logging
import threading
from functools import wraps

import sqlalchemy as sa

import ping
from db import init_db
from app import create_app

DB_URL = os.environ.get("DB_URL")
ENVIRONMENT = os.environ.get("FLASK_ENV", "development")
PING_HOSTS = os.environ.get("PING_HOSTS", "google.com")
PING_DELAY_SEC = int(os.environ.get("PING_DELAY_SEC", 60))
PING_FAIL_DELAY_SEC = PING_DELAY_SEC // 10 or 1

DEBUG = ENVIRONMENT == "development"

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(lineno)-4s <%(funcName)s> - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
logger.info("Starting ping %s in %s environment", PING_HOSTS, ENVIRONMENT)
logger.debug(
    "PING_DELAY_SEC=%r, PING_FAIL_DELAY_SEC=%r", PING_DELAY_SEC, PING_FAIL_DELAY_SEC
)

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


def log_res(res):
    """Save ping res to db

    Args:
        res (ping.PingResult): Ping result instance
    """
    with db.session():
        db.Ping.create(res.host, res.time_ms, int(time.time()))


@run_as_thread
def ping_tester(host, delay=60, delay_fail=6):
    """Ping testing thread

    Args:
        host (str): Ping hostname or IP
        delay (int, optional): Delay between ping requests
        delay_fail (int, optional): Delay between ping requests when prev ping fails
    """
    while True:
        res = ping.ping(host)
        if not res.ok:
            logger.warning("Ping failed: %s", res)
            sub_res = ping.ping(host)  # Double check ping if it fails
            while not sub_res.ok:
                log_res(sub_res)
                sub_res = ping.ping(host)
                time.sleep(delay_fail)
            log_res(sub_res)
        else:
            log_res(res)

        time.sleep(delay)


if __name__ == "__main__":
    for host in {h for h in PING_HOSTS.split(",")}:
        logger.info("Run ping tester for %s", host)
        ping_tester(host, delay=PING_DELAY_SEC, delay_fail=PING_FAIL_DELAY_SEC)

    app = create_app()
    app.run(host="0.0.0.0")
