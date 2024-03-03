from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from website import app, db
from website.projects.forms import (
    CreateProjectForm,
    AddTaskForm,
    EditProjectForm,
    ManageMembersForm,
)
from website.projects.models import Project

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects")
@login_required
def projects():
    projects = Project.query.all()
    return render_template("projects/projects.html", projects=projects)


@projects_bp.route("/projects/create", methods=["GET", "POST"])
@login_required
def create_project():
    form = CreateProjectForm()
    if form.validate_on_submit():
        project = Project(name=form.name.data, description=form.description.data)
        db.session.add(project)
        db.session.commit()

        flash("Project created successfully", "success")
        return redirect(url_for("projects.projects"))

    return render_template("projects/create_project.html", form=form)


@projects_bp.route("/projects/<int:project_id>")
@login_required
def project_details(project_id):
    project = Project.query.get(project_id)
    if project is None:
        flash("Project not found", "danger")
        return redirect(url_for("projects.projects"))

    form = CreateProjectForm()
    return render_template("projects/project_details.html", project=project, form=form)


@projects_bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get(project_id)
    if project is None:
        flash("Project not found", "danger")
        return redirect(url_for("projects.projects"))

    form = EditProjectForm()
    if form.validate_on_submit():
        form.populate_obj(project)
        db.session.commit()

        flash("Project updated successfully", "success")
        return redirect(url_for("projects.project_details", project_id=project_id))

    form.name.data = project.name
    form.description.data = project.description

    return render_template("projects/edit_project.html", project=project, form=form)


@projects_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    project = Project.query.get(project_id)
    if project is None:
        flash("Project not found", "danger")
        return redirect(url_for("projects.projects"))

    db.session.delete(project)
    db.session.commit()

    flash("Project deleted successfully", "success")
    return redirect(url_for("projects.projects"))
