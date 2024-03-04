from datetime import datetime
import os

from flask import (
    Blueprint,
    app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from website import bcrypt, db
from website.accounts.models import Profile, User
from website.accounts.token import confirm_token, generate_token
from website.utils.decorators import logout_required
from website.utils.email import send_email

from .forms import LoginForm, ProfileForm, RegisterForm

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("/register", methods=["GET", "POST"])
@logout_required
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)

        db.session.add(user)
        db.session.commit()

        token = generate_token(user.email)
        confirm_url = url_for("accounts.confirm_email", token=token, _external=True)
        html = render_template("accounts/confirm_email.html", confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(user.email, subject, html)

        login_user(user)

        flash("A confirmation email has been sent via email.", "success")
        return redirect(url_for("accounts.inactive"))

    return render_template("accounts/register.html", form=form)


@accounts_bp.route("/login", methods=["GET", "POST"])
@logout_required
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("core.home"))
        else:
            flash("Invalid email and/or password.", "danger")
            return render_template("accounts/login.html", form=form)
    return render_template("accounts/login.html", form=form)


@accounts_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logged out.", "success")
    return redirect(url_for("accounts.login"))


@accounts_bp.route("/confirm/<token>")
@login_required
def confirm_email(token):
    if current_user.is_confirmed:
        flash("Account already confirmed.", "success")
        return redirect(url_for("core.home"))
    email = confirm_token(token)
    user = User.query.filter_by(email=current_user.email).first_or_404()
    if user.email == email:
        user.is_confirmed = True
        user.confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("You have confirmed your account. Thanks!", "success")
    else:
        flash("The confirmation link is invalid or has expired.", "danger")
    return redirect(url_for("core.home"))


@accounts_bp.route("/inactive")
@login_required
def inactive():
    if current_user.is_confirmed:
        return redirect(url_for("core.home"))
    return render_template("accounts/inactive.html")


@accounts_bp.route("/resend")
@login_required
def resend_confirmation():
    if current_user.is_confirmed:
        flash("Your account has already been confirmed.", "success")
        return redirect(url_for("core.home"))
    token = generate_token(current_user.email)
    confirm_url = url_for("accounts.confirm_email", token=token, _external=True)
    html = render_template("accounts/confirm_email.html", confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash("A new confirmation email has been sent.", "success")
    return redirect(url_for("accounts.inactive"))


@accounts_bp.route("/profile")
@login_required
def profile():
    profile = current_user.profile
    return render_template("accounts/profile.html", profile=profile)


@accounts_bp.route("/profile/create", methods=["GET", "POST"])
@login_required
def create_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        profile = Profile(
            user_id=current_user.id,
            full_name=form.full_name.data,
            age=form.age.data,
            bio=form.bio.data,
        )
        if form.profile_photo.data:
            filename = secure_filename(form.profile_photo.data.filename)
            form.profile_photo.data.save(
                os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            )
            profile.photo = filename

        db.session.add(profile)
        db.session.commit()
        flash("Profile created successfully", "success")
        return redirect(url_for("accounts.profile"))

    return render_template("accounts/create_profile.html", form=form)


@accounts_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    profile = current_user.profile

    form = ProfileForm(obj=profile)
    if form.validate_on_submit():
        form.populate_obj(profile)
        if form.profile_photo.data:
            filename = secure_filename(form.profile_photo.data.filename)
            form.profile_photo.data.save(
                os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            )
            profile.photo = filename

        db.session.commit()
        flash("Profile updated successfully", "success")
        return redirect(url_for("accounts.profile"))

    return render_template("accounts/edit_profile.html", form=form, profile=profile)


@accounts_bp.route("/profile/delete_photo", methods=["POST"])
@login_required
def delete_profile_photo():
    if current_user.profile.photo:
        os.remove(
            os.path.join(
                current_app.config["UPLOAD_FOLDER"], current_user.profile.photo
            )
        )
        current_user.profile.photo = None
        db.session.commit()
        flash("Profile photo deleted successfully", "success")
    return redirect(url_for("accounts.edit_profile"))
