from flask import Flask, g, request
from flask_sqlalchemy import SQLAlchemy
from config.config import Config
import logging

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


from app.routes.health_routes import health_bp
from app.routes.user_routes import user_bp
from app.routes.order_routes import order_bp
from app.routes.general_routes import general_bp


app.register_blueprint(health_bp)
app.register_blueprint(user_bp)
app.register_blueprint(order_bp)
app.register_blueprint(general_bp)


def api_key_required():
    if request.path == '/':
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        return None
    
    #api_key = request.headers.get("API-KEY")
    #if api_key != Config.API_KEY:
    #    return {
    #        "message": "Unauthorized access, invalid API key",
    #    }, 500
    

@app.before_request
def handle_before_request():
    g.db_session = db.session
    return api_key_required()


@app.teardown_request
def teardown_request(exception=None):
    db_session = getattr(g, 'db_session', None)
    if db_session:
        db_session.remove()