from decouple import config
from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object(config("APP_SETTINGS", default="config.DevelopmentConfig"))
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from website.accounts.views import accounts_bp
from website.core.views import core_bp
from website.projects.views import projects_bp
from website.tasks.views import tasks_bp

app.register_blueprint(accounts_bp)
app.register_blueprint(core_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(tasks_bp)

from .accounts.models import User
from .projects.models import Project, Task, ProjectMember, Comment

login_manager.login_view = "accounts.login"
login_manager.login_message_category = "danger"


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()


@app.errorhandler(401)
def unauthorized_page(error):
    return render_template("errors/401.html"), 401


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500
