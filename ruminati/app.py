from contextlib import contextmanager
from datetime import tzinfo

from dateutil.tz import gettz, UTC
from flask import Flask, current_app, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ruminati.models import Base
from ruminati.picker import blueprint as picker
from ruminati.utils import assert_naive


def geolocation(app):
    @app.before_request
    def get_user_timezone():
        if request.remote_addr in ("127.0.0.1", "localhost"):
            request.user_tz = gettz()
        else:
            request.user_tz = current_app.config["EVENT_TIMEZONE"]


def database(app):
    engine = create_engine(app.config["DATABASE_URI"], echo=True)
    Session = sessionmaker(bind=engine)

    @contextmanager
    def session_scope():
        db_sess = Session()
        try:
            yield db_sess
            db_sess.commit()
        except Exception as ex:
            db_sess.rollback()
            raise
        finally:
            db_sess.close()

    app.session_scope = session_scope

    @app.before_request
    def setup_session():
        request.db_sess = Session()

    @app.after_request
    def close_session(response):
        request.db_sess.close()
        return response

    return engine


def commands(app, engine):
    @app.cli.command()
    def init_db():
        Base.metadata.create_all(engine)


class Config(object):
    DATABASE_URI = "sqlite:///:memory:"
    EVENT_TIMEZONE = UTC,
    EVENT_START = None
    EVENT_END = None
    SUBDIV = 2
    MAXDIV = 2


def create_app(config=Config()):
    app = Flask(__name__)

    app.config.from_object(config)
    app.config.from_envvar("RUMINATI_CONFIG", silent=True)

    event_tz = app.config["EVENT_TIMEZONE"]
    assert isinstance(event_tz, tzinfo)

    assert_naive(app.config["EVENT_START"])
    assert_naive(app.config["EVENT_END"])

    app.config.update(BRKBEG=app.config["EVENT_START"].replace(tzinfo=event_tz),
                      BRKEND=app.config["EVENT_END"].replace(tzinfo=event_tz))

    geolocation(app)
    engine = database(app)
    commands(app, engine)

    app.register_blueprint(picker)
    return app
