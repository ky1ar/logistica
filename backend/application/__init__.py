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
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

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
    

def reconnect_db():
    if not hasattr(g, "db_session"):
        g.db_session = db.session

    try:
        g.db_session.execute(text("SELECT 1")) 
    except OperationalError:
        db.engine.dispose() 
        g.db_session.remove()
        g.db_session = db.session


@app.before_request
def before_request():
    if request.path == "/":
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)

    reconnect_db()


@app.teardown_request
def teardown_request(exception=None):
    db_session = getattr(g, 'db_session', None)
    if db_session:
        db_session.remove()