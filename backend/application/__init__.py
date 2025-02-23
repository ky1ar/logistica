import logging
import eventlet
import redis

eventlet.monkey_patch()

from config import Config, Redis
from flask import Flask, g, request
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config.from_object(Config)


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins='*')
redis_client = redis.StrictRedis.from_url(Redis.URL, decode_responses=True)


from application.routes import blueprint
app.register_blueprint(blueprint)


def api_key_required():
    if request.path == '/':
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        return None
    

@app.before_request
def handle_before_request():
    g.db_session = db.session
    return api_key_required()


@app.teardown_request
def teardown_request(exception=None):
    db_session = getattr(g, 'db_session', None)
    if db_session:
        db_session.remove()