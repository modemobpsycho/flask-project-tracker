from flask import Blueprint, render_template
from flask_login import login_required
from website.projects.models import Project

from website.utils.decorators import check_is_confirmed

core_bp = Blueprint("core", __name__)


@core_bp.route("/")
@login_required
@check_is_confirmed
def home():
    projects = Project.query.all()
    return render_template("core/index.html", projects=projects)
