from behave_http.environment import before_scenario

from example.app import app
from example.models import db


def before_all(context):
    context.app = app
    context._ctx = app.test_request_context()
    context._ctx.push()


def after_all(context):
    db.session.close()
    db.session.remove()
    context._ctx.pop()
