from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_appbuilder import AppBuilder
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
appbuilder = AppBuilder()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    csrf.init_app(app)
    with app.app_context():
        appbuilder.init_app(app, db.session)
        from .views import register_views
        register_views(appbuilder)
        from .routes import bp
        app.register_blueprint(bp)
    return app
