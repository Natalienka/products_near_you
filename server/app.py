# -*- coding: utf-8 -*-

import os
from flask import Flask
from server.api import api
from server.database import Database

def create_app(settings_overrides=None):
    app = Flask(__name__)
    configure_settings(app, settings_overrides)
    configure_blueprints(app)
    load_data(app)
    return app


def configure_settings(app, settings_override):
    parent = os.path.dirname(__file__)
    data_path = os.path.join(parent, '..', 'data')
    app.config.update({
        'DEBUG': True,
        'TESTING': False,
        'DATA_PATH': data_path
    })
    if settings_override:
        app.config.update(settings_override)

def configure_blueprints(app):
    app.register_blueprint(api)

def load_data(app):
    database = Database()
    database.load(app.config['DATA_PATH'])
    app.config.update({
        'DATABASE': database
    })
