from .DataBase import db as System_FileDB
from .DataBase import login_manager

import os


def init_app(app):
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'System_File.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    System_FileDB.init_app(app)
    login_manager.init_app(app)

    
    with app.app_context():
        System_FileDB.create_all()



from .routes.demo import bp as demo_bp
from .routes.user_service import bp as user_service_bp

def create_app(app1):

    app1.register_blueprint(user_service_bp)
    init_app(app1)
    return app1