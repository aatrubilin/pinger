import time
import logging
import datetime

import sqlalchemy as sa
from flask import Blueprint, render_template, jsonify, request

from db import get_db

logger = logging.getLogger(__name__)

bp = Blueprint("app", __name__, template_folder="../templates")

dt_sep = " - "


def _dt_to_ts(dt):
    return time.mktime(dt.timetuple())


def _parse_dt_range(dt):
    logger.info("dt = %r", dt)
    if dt is None:
        dt = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time())
        query_range = (_dt_to_ts(dt), _dt_to_ts(dt + datetime.timedelta(days=1)))
        dt_picker_value = dt.date().isoformat()
    else:
        dt = dt.split(dt_sep)
        if len(dt) == 1:
            dt = datetime.datetime.combine(
                datetime.date.fromisoformat(dt[0]), datetime.time()
            )
            query_range = (_dt_to_ts(dt), _dt_to_ts(dt + datetime.timedelta(days=1)))
            dt_picker_value = dt.date().isoformat()
        else:
            dt_start = datetime.datetime.combine(
                datetime.date.fromisoformat(dt[0]), datetime.time()
            )
            dt_end = datetime.datetime.combine(
                datetime.date.fromisoformat(dt[1]), datetime.time()
            ) + datetime.timedelta(days=1)
            query_range = (_dt_to_ts(dt_start), _dt_to_ts(dt_end))
            dt_picker_value = (
                f"{dt_start.date().isoformat()}{dt_sep}{dt_end.date().isoformat()}"
            )

    return dt_picker_value, query_range


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
    return render_template("index.html", dt=dt_picker_value, min_date=min_date.isoformat())


@bp.route("/getData", methods=["GET", "POST"])
def get_data():
    db = get_db()
    logger.info("args: %s", request.args)
    _, query_range = _parse_dt_range(request.args.get("dt"))

    data_ = {}
    for row in db.Ping.query.filter(
        sa.and_(db.Ping.ts >= query_range[0], db.Ping.ts < query_range[1])
    ).order_by(db.Ping.ts):
        if row.host not in data_:
            data_[row.host] = []

        data_[row.host].append((int(row.ts * 1e3), row.ping))
    data = [
        {"name": host, "type": "area", "data": data} for host, data in data_.items()
    ]
    return jsonify(data)
