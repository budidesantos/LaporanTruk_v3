import inspect
from weakref import ref
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

db = SQLAlchemy()

bcrypt = Bcrypt()

db_name = 'test'
username = 'root'
password = ''

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '123123'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@localhost/{db_name}'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    }
    db.init_app(app)
    bcrypt.init_app(app)

    from .auth import auth
    from .main.routes import main
    from .truk_supply.routes import supply
    from .truk_sewa.routes import sewa
    from .models import User
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(supply)
    app.register_blueprint(sewa)

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    try:
        db.create_all(app=app)

    except:
        print("error!")

#     if not path.exists('website/' + DB_NAME):
#         db.create_all(app=app)
        
#         print('Database dibuat!')

