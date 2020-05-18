import time
import logging
import datetime

import sqlalchemy as sa
from flask import Blueprint, render_template, jsonify, request

from db import get_db

logger = logging.getLogger(__name__)

bp = Blueprint("app", __name__, template_folder="../templates")

dt_sep = " - "
dt_day = datetime.timedelta(days=1) - datetime.timedelta(microseconds=1)


def _dt_to_ts(dt):
    return time.mktime(dt.timetuple())


def _parse_dt_range(dt):
    if dt:
        dt = dt.split(dt_sep)
        if len(dt) == 1:
            dt_start = datetime.datetime.combine(
                datetime.date.fromisoformat(dt[0]), datetime.time()
            )
            query_range = (dt_start, dt_start + dt_day)
            dt_picker_value = dt_start.date().isoformat()
        else:
            dt_start = datetime.datetime.combine(
                datetime.date.fromisoformat(dt[0]), datetime.time()
            )
            dt_end = (
                datetime.datetime.combine(
                    datetime.date.fromisoformat(dt[1]), datetime.time()
                )
                + dt_day
            )
            query_range = (dt_start, dt_end)
            dt_picker_value = (
                f"{dt_start.date().isoformat()}{dt_sep}{dt_end.date().isoformat()}"
            )
    else:
        dt = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time())
        query_range = (dt, dt + dt_day)
        dt_picker_value = dt.date().isoformat()

    query_range_ts = _dt_to_ts(query_range[0]), _dt_to_ts(query_range[1])
    logger.debug(
        "dt: %s; query_range: %s: %s, %s: %s",
        dt,
        query_range[0],
        query_range_ts[0],
        query_range[1],
        query_range_ts[1],
    )
    return dt_picker_value, query_range_ts


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
def index():
    db = get_db()
    first_row = db.Ping.query.order_by(db.Ping.ts).limit(1).first()
    if first_row:
        min_date = datetime.datetime.fromtimestamp(first_row.ts).date()
    else:
        min_date = datetime.datetime.now().date()

    dt_picker_value, _ = _parse_dt_range(request.args.get("dt"))
    return render_template(
        "index.html", dt=dt_picker_value, min_date=min_date.isoformat()
    )


@bp.route("/getData", methods=["GET", "POST"])
def get_data():
    db = get_db()
    logger.info("args: %s", request.args)
    _, query_range = _parse_dt_range(request.args.get("dt"))

    data_ = {}
    no_ping_sec = 0
    prev_no_ping_ts = 0
    for row in db.Ping.query.filter(
        sa.and_(db.Ping.ts >= query_range[0], db.Ping.ts < query_range[1])
    ).order_by(db.Ping.ts):
        if row.host not in data_:
            data_[row.host] = []

        if row.ping <= 0:
            if prev_no_ping_ts:
                no_ping_sec += row.ts - prev_no_ping_ts
            prev_no_ping_ts = row.ts
        else:
            prev_no_ping_ts = 0

        data_[row.host].append((int(row.ts * 1e3), row.ping))

    if no_ping_sec:
        no_ping = str(datetime.timedelta(seconds=no_ping_sec))
    else:
        no_ping = None

    data = {
        "data": [
            {"name": host, "type": "line", "data": data} for host, data in data_.items()
        ],
        "no_ping": no_ping,
    }
    return jsonify(data)
