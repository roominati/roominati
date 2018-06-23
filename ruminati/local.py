from datetime import timedelta

import click

from ruminati.models import Breakout
from ruminati.utils import parse_naive_datetime, parse_aware_datetime
from ruminati.app import create_app as real_create_app, Config
from dateutil.tz import gettz


local_tz = gettz()


class LocalConfig(Config):
    DATABASE_URI = "sqlite:///local.sqlite3"
    EVENT_TIMEZONE = local_tz
    EVENT_START = parse_naive_datetime("01/01/2018 08:00 AM")
    EVENT_END = parse_naive_datetime("01/01/2018 04:30 PM")
    SUBDIV = 2
    MAXDIV = 2


def local_commands(app):
    @app.cli.command()
    @click.argument("name")
    @click.argument("start_at")
    @click.argument("duration")
    def create_breakout(self, name, start_at, duration):
        """Create a breakout model.

        START_AT is parsed in your local timezone.
        DURATION is an integer number of minutes.
        """
        with app.session_scope() as db_sess:
            stamp = parse_aware_datetime(start_at, local_tz)
            db_sess.add(Breakout(name=name, start_at=stamp,
                                 duration=timedelta(minutes=int(duration))))
            db_sess.commit()

    @app.cli.command()
    def interesting_data():
        with app.session_scope() as db_sess:
            dt = parse_aware_datetime("01/01/2018 08:00 AM", local_tz)
            db_sess.add(Breakout(name="Event One", start_at=dt,
                                 duration=timedelta(minutes=60),
                                 description="This is my first event."))

            dt = parse_aware_datetime("01/01/2018 01:00 PM", local_tz)
            db_sess.add(Breakout(name="Event Two", start_at=dt,
                                 duration=timedelta(minutes=60),
                                 description="this is my second event."))


def create_app():
    app = real_create_app(LocalConfig())
    local_commands(app)
    return app

