import os
import time
import logging

import statsd

from ping import ping

ENVIRONMENT = os.environ.get("PING_ENV", "prod")
DEBUG = ENVIRONMENT.lower() == "dev"
HOST = os.environ.get("PING_HOST", "google.com")

statsd_client = statsd.StatsClient(
    host=os.environ.get("STATSD_HOST", "127.0.0.1"),
    port=int(os.environ.get("STATSD_PORT", 8125)),
    prefix=os.environ.get("STATSD_PREFIX", "ping"),
)

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(lineno)-4s <%(funcName)s> - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

logger.info("Starting ping %s in %s environment", HOST, ENVIRONMENT)

while True:
    res = ping(HOST)
    logger.debug("%s: %s", res.host, res.time_ms)
    statsd_client.set(res.host, res.time_ms)
    time.sleep(1)
