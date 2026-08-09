from flask import Flask
from models import db,User 
from config import *
from flask_login import LoginManager

app=None
login_manager=None

# CAN WE DO ALL THE THINGS IN THIS setup_app() FUNC WITHOUT DEFINING THE FUNC def setup_app() ?
def setup_app():
    global app,login_manager
    app=Flask(__name__)

    app.config["SECRET_KEY"]=SECRET_KEY
    login_manager=LoginManager()
    login_manager.init_app(app)

    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///tma.sqlite3"
    app.url_map.strict_slashes = False  
    db.init_app(app)
    app.app_context().push()

setup_app()

@login_manager.user_loader
def load_user(userID):
    return User.query.get(int(userID))

from controller import *
if __name__=="__main__":
    app.run(debug=True)


# Upcoming Treks in admin_dashboard
# date, trekLocation, trekStaff, trekker