import os
import re
import logging
import subprocess

logger = logging.getLogger(__name__)

if os.name == "nt":
    __encoding = os.environ.get("PING_ENCODING", "cp866")
    __param = "-n"
    __res_line = 2
    time_regexp = re.compile(r"время=([\d]+)мс")
else:
    __encoding = os.environ.get("PING_ENCODING", "utf8")
    __param = "-c"
    __res_line = 1
    time_regexp = re.compile(r"time=([\d.]+) ms")  # 64 bytes from 173.194.222.113: seq=0 ttl=38 time=66.077 ms


class PingResult(object):
    def __init__(self, host, out, error):
        self.host = host
        self.out = out
        self.error = error

        self.time_ms = -1.0

        self._parse_out()

    def _parse_out(self):
        if not self.error:
            try:
                self.time_ms = float(time_regexp.search(self.out).group(1))
            except:
                self.time_ms = -2.0
                logger.exception("Unhandled exception when parsing out: %s", self.out)

    @property
    def ok(self):
        return self.time_ms >= 0

    def __repr__(self):
        return "<PingResult({s.host!r}, {s.time_ms})>".format(s=self)


def ping(host=None):
    host = host or "google.com"

    try:
        out = subprocess.check_output(
            ("ping", __param, "1", host), universal_newlines=True, encoding=__encoding
        )
        error = False
    except subprocess.CalledProcessError as err:

        out = err.output
        error = True

    try:
        out = out.splitlines()[__res_line]
    except IndexError:
        error = True

    res = PingResult(host, out, error)

    return res
