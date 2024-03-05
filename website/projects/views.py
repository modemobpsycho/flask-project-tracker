from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from website import app, db
from website.accounts.models import User, Profile
from website.projects.forms import (
    CreateProjectForm,
    AddTaskForm,
    EditProjectForm,
    ManageMembersForm,
    SendJoinRequestForm,
    AcceptRequestForm,
    RejectRequestForm,
    InviteMemberForm,
)
from website.projects.models import (
    Project,
    Task,
    JoinRequest,
    ProjectMember,
    Comment,
)
from website.tasks.forms import TaskForm
from sqlalchemy import or_

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects")
@login_required
def projects():
    user_projects = Project.query.filter_by(creator_id=current_user.id).all()
    return render_template("projects/projects.html", projects=user_projects)


@projects_bp.route("/projects/create", methods=["GET", "POST"])
@login_required
def create_project():
    form = CreateProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            description=form.description.data,
            creator_id=form.creator_id.data,
            visibility=form.visibility.data,
        )
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

    is_creator = current_user.id == project.creator_id
    is_public = project.visibility == "public"
    can_view = is_public or is_creator
    can_edit = is_creator

    if not can_view:
        flash("You are not allowed to view this project", "danger")
        return redirect(url_for("projects.projects"))

    form = CreateProjectForm() if can_edit else None
    send_request_form = SendJoinRequestForm() if not is_creator else None
    invite_member_form = InviteMemberForm()
    creator_profile = Profile.query.filter_by(user_id=project.creator_id).first()
    project_creator = User.query.get(project.creator_id)

    project_members = ProjectMember.query.filter_by(project_id=project_id).all()
    members_info = []
    for member in project_members:
        member_profile = Profile.query.filter_by(user_id=member.user_id).first()
        member_user = User.query.get(member.user_id)
        members_info.append(
            {"user": member_user, "profile": member_profile, "role": member.role}
        )

    return render_template(
        "projects/project_details.html",
        project=project,
        form=form,
        tasks=project.tasks,
        creator=creator_profile,
        project_creator=project_creator,
        can_edit=can_edit,
        is_owner=is_creator,
        send_request_form=send_request_form,
        project_members=members_info,
        invite_member_form=invite_member_form,
    )


@projects_bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get(project_id)
    if project is None:
        flash("Project not found", "danger")
        return redirect(url_for("projects.projects"))

    form = EditProjectForm(obj=project)
    if form.validate_on_submit():
        form.populate_obj(project)
        db.session.commit()

        flash("Project updated successfully", "success")
        return redirect(url_for("projects.project_details", project_id=project_id))

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


@projects_bp.route("/project/<int:project_id>/create_task", methods=["GET", "POST"])
def create_task(project_id):
    project = Project.query.get_or_404(project_id)
    form = TaskForm()

    if form.validate_on_submit():
        task = Task(
            name=form.name.data,
            description=form.description.data,
            status=form.status.data,
            project_id=project_id,
        )
        db.session.add(task)
        db.session.commit()
        return redirect(url_for("projects.project_details", project_id=project_id))

    return render_template("tasks/create_task.html", form=form, project=project)


@projects_bp.route("/public_projects")
def public_projects():
    public_projects = Project.query.filter_by(visibility="public").all()
    return render_template(
        "projects/public_projects.html", public_projects=public_projects
    )


@projects_bp.route("/join_requests")
@login_required
def join_requests():
    outgoing_requests = []
    incoming_requests = []

    # Получаем все запросы пользователя
    all_requests = JoinRequest.query.filter(
        or_(
            JoinRequest.sender_id == current_user.id,
            JoinRequest.user_id == current_user.id,
        )
    ).all()

    project_ids = set(request.project_id for request in all_requests)
    projects = {
        project.id: project
        for project in Project.query.filter(Project.id.in_(project_ids)).all()
    }

    for request in all_requests:
        if (
            request.sender_id == current_user.id
            or request.sender_id == projects[request.project_id].creator_id
        ):
            outgoing_requests.append(request)
        else:
            incoming_requests.append(request)

    accept_form = AcceptRequestForm()
    reject_form = RejectRequestForm()

    return render_template(
        "projects/projects_requests.html",
        outgoing_requests=outgoing_requests,
        incoming_requests=incoming_requests,
        accept_form=accept_form,
        reject_form=reject_form,
    )


@projects_bp.route("/send_request/<int:project_id>", methods=["GET", "POST"])
@login_required
def send_request(project_id):
    project = Project.query.get(project_id)
    if project is None:
        flash("Project not found", "danger")
        return redirect(url_for("projects.projects"))

    form = SendJoinRequestForm()
    if form.validate_on_submit():
        # Определяем отправителя запроса
        sender_id = current_user.id

        # Если запрос отправлен создателем проекта, устанавливаем user_id в ID текущего пользователя
        # И sender_id в ID создателя проекта
        if current_user.id != project.creator_id:
            sender_id = project.creator_id

        request = JoinRequest(
            user_id=current_user.id,  # Здесь user_id будет либо ID текущего пользователя (если запрос отправлен создателем),
            # либо ID пользователя, отправившего запрос (если запрос отправлен другим пользователем)
            project_id=project_id,
            sender_id=sender_id,
            message=form.message.data,
            role=form.role.data,
        )
        db.session.add(request)
        db.session.commit()
        flash("Join request sent successfully", "success")
        return redirect(url_for("projects.project_details", project_id=project_id))

    return render_template(
        "projects/send_request.html", form=form, project_id=project_id
    )


@projects_bp.route("/accept_request/<int:request_id>", methods=["POST"])
@login_required
def accept_join_request(request_id):
    request = JoinRequest.query.get(request_id)
    if request is None:
        flash("Request not found", "danger")
        return redirect(url_for("projects.join_requests"))

    project = Project.query.get(request.project_id)
    if project is None:
        flash("Project not found", "danger")
        return redirect(url_for("projects.join_requests"))

    # Проверяем sender_type, чтобы определить, был ли запрос отправлен текущим пользователем или создателем проекта
    if request.sender_type == "user":
        # Если запрос отправлен текущим пользователем, то устанавливаем его user_id как отправителя
        sender_id = current_user.id
    else:
        # Если запрос отправлен создателем проекта, то устанавливаем его sender_id как отправителя
        sender_id = request.sender_id

    # Создаем нового участника проекта
    project_member = ProjectMember(
        user_id=request.user_id,  # Используем user_id из запроса
        project_id=request.project_id,
        role=request.role,
    )
    db.session.add(project_member)

    # Удаляем запрос на присоединение
    db.session.delete(request)
    db.session.commit()

    flash("Join request accepted successfully", "success")
    return redirect(url_for("projects.join_requests"))


@projects_bp.route("/reject_request/<int:request_id>", methods=["POST"])
@login_required
def reject_join_request(request_id):
    request = JoinRequest.query.get(request_id)
    if request is None:
        flash("Request not found", "danger")
        return redirect(url_for("projects.join_requests"))

    # Удаляем запрос на присоединение
    db.session.delete(request)
    db.session.commit()

    flash("Join request rejected successfully", "success")
    return redirect(url_for("projects.join_requests"))


@projects_bp.route(
    "/projects/<int:project_id>/remove_member/<int:member_id>", methods=["POST"]
)
@login_required
def remove_member_from_project(project_id, member_id):
    project = Project.query.get(project_id)
    if project is None:
        flash("Project not found", "danger")
        return redirect(url_for("projects.projects"))

    if current_user.id != project.creator_id:
        flash("Only the project creator can remove members", "danger")
        return redirect(url_for("projects.project_details", project_id=project_id))

    member = ProjectMember.query.filter_by(
        project_id=project_id, user_id=member_id
    ).first()
    if member is None:
        flash("Member not found in the project", "danger")
        return redirect(url_for("projects.project_details", project_id=project_id))

    db.session.delete(member)
    db.session.commit()
    flash("Member removed from the project", "success")
    return redirect(url_for("projects.project_details", project_id=project_id))


@projects_bp.route("/projects/<int:project_id>/invite", methods=["POST"])
@login_required
def invite_member(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user.id != project.creator_id:
        abort(403)  # Forbidden

    invite_form = InviteMemberForm(request.form)
    if invite_form.validate_on_submit():
        email = invite_form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            join_request = JoinRequest(
                project_id=project.id,
                user_id=user.id,
                sender_id=current_user.id,  # Устанавливаем sender_id в идентификатор текущего пользователя (приглашающего)
                sender_type="creator",  # Устанавливаем тип отправителя как "creator"
                role="Member",
            )
            db.session.add(join_request)
            db.session.commit()
            flash(f"User {user.email} has been invited to the project.", "success")
        else:
            flash(f"No user found with email {email}.", "danger")
    else:
        flash_errors(invite_form)

    return redirect(url_for("projects.project_details", project_id=project.id))
