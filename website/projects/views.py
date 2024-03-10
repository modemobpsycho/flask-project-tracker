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
    user_created_projects = Project.query.filter_by(creator_id=current_user.id).all()
    user_member_projects = (
        Project.query.join(Project.members)
        .filter(
            ProjectMember.user_id == current_user.id,
            ProjectMember.user_id != Project.creator_id,
        )
        .all()
    )
    return render_template(
        "projects/projects.html",
        created_projects=user_created_projects,
        member_projects=user_member_projects,
    )


@projects_bp.route("/projects/create", methods=["GET", "POST"])
@login_required
def create_project():
    form = CreateProjectForm()
    if form.validate_on_submit():
        existing_project = Project.query.filter_by(
            creator_id=current_user.id,
            name=form.name.data,
        ).first()

        if existing_project:
            flash("You already have a project with this name", "danger")
            return redirect(url_for("projects.create_project"))

        project = Project(
            name=form.name.data,
            description=form.description.data,
            creator_id=current_user.id,
            visibility=form.visibility.data,
        )
        db.session.add(project)
        db.session.commit()

        role = "creator"
        project_member = ProjectMember(
            user_id=current_user.id,
            project_id=project.id,
            role=role,
        )
        db.session.add(project_member)
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
    is_member = any(member.user_id == current_user.id for member in project_members)
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
        is_member=is_member,
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

    all_requests = JoinRequest.query.filter(
        or_(
            JoinRequest.sender_id == current_user.id,
            JoinRequest.user_id == current_user.id,
        )
    ).all()

    for request in all_requests:
        if request.sender_type == "creator":
            if request.sender_id == current_user.id:
                outgoing_requests.append(request)
            else:
                incoming_requests.append(request)
        elif request.sender_type == "user":
            if request.user_id == current_user.id:
                incoming_requests.append(request)
            else:
                outgoing_requests.append(request)

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
    creator_id = project.creator_id
    if project is None:
        flash("Project not found", "danger")
        return redirect(url_for("projects.projects"))
    user = User.query.get(current_user.id)
    join_request = JoinRequest.query.filter_by(
        sender_id=current_user.id, project_id=project.id
    ).first()
    form = SendJoinRequestForm()
    if form.validate_on_submit():
        if join_request is None:
            sender_type = "user"
            request = JoinRequest(
                user_id=creator_id,
                project_id=project_id,
                sender_id=current_user.id,
                sender_type=sender_type,
                message=form.message.data,
                role=form.role.data,
            )
            db.session.add(request)
            db.session.commit()
            flash("Join request sent successfully", "success")
            return redirect(url_for("projects.project_details", project_id=project_id))
        else:
            flash(f"You have already sent a join request to {project.name}", "danger")
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

    if request.sender_type == "creator":
        sender_id = project.creator_id
        user_id = request.user_id
    else:
        sender_id = request.user_id
        user_id = request.sender_id

    project_member = ProjectMember(
        user_id=user_id,
        project_id=request.project_id,
        role=request.role,
    )
    db.session.add(project_member)

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
        abort(403)

    invite_form = InviteMemberForm(request.form)
    if invite_form.validate_on_submit():
        email = invite_form.email.data
        user_exists = db.session.query(
            User.query.filter_by(email=email).exists()
        ).scalar()
        if user_exists:
            user = User.query.filter_by(email=email).first()
            project_member = ProjectMember.query.filter_by(
                user_id=user.id, project_id=project_id
            ).first()
            join_request = JoinRequest.query.filter_by(
                user_id=user.id, project_id=project.id
            ).first()
            is_creator = current_user.id == project.creator_id
            if project_member is None and join_request is None and not is_creator:
                join_request = JoinRequest(
                    project_id=project.id,
                    user_id=user.id,
                    sender_id=current_user.id,
                    sender_type="creator",
                    role="Member",
                )
                db.session.add(join_request)
                db.session.commit()
                flash(f"User {user.email} has been invited to the project.", "success")
            else:
                flash(f"This user {email} already exists in project members", "danger")
        else:
            flash(f"No user found with email {email}.", "danger")
    else:
        flash(f"Smth wrong", "danger")

    return redirect(url_for("projects.project_details", project_id=project.id))
