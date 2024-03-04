from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from website import app, db

from website.projects.models import Task
from website.tasks.forms import TaskForm

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/task/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm(obj=task)

    if form.validate_on_submit():
        form.populate_obj(task)
        db.session.commit()
        return redirect(url_for("projects.project_details", project_id=task.project_id))

    return render_template("tasks/edit_task.html", form=form, task=task)


@tasks_bp.route("/task/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("projects.project_details", project_id=task.project_id))
