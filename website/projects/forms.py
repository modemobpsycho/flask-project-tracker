from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    HiddenField,
    SelectField,
    StringField,
    TextAreaField,
    SubmitField,
    IntegerField,
)
from wtforms.validators import DataRequired, Email


class AddTaskForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Add")


class CreateProjectForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    visibility = SelectField(
        "Visibility",
        choices=[("public", "Public"), ("private", "Private")],
        default="public",
        validators=[DataRequired()],
    )
    creator_id = HiddenField("Creator ID", default=None)
    submit = SubmitField("Create")

    def __init__(self, *args, **kwargs):
        super(CreateProjectForm, self).__init__(*args, **kwargs)
        if current_user.is_authenticated:
            self.creator_id.data = current_user.id


class ManageMembersForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    role = StringField("Role")
    submit_add = SubmitField("Add Member")
    submit_remove = SubmitField("Remove Member")


class EditProjectForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    visibility = SelectField(
        "Visibility",
        choices=[("public", "Public"), ("private", "Private")],
        validators=[DataRequired()],
    )


class AddProjectMemberForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    role = StringField("Role")
    submit = SubmitField("Add Member")


class RemoveProjectMemberForm(FlaskForm):
    member_id = StringField("Member ID", validators=[DataRequired()])
    submit = SubmitField("Remove Member")


class SendJoinRequestForm(FlaskForm):
    message = StringField("Message", validators=[DataRequired()])
    role = StringField("Role", validators=[DataRequired()])
    sender_id = IntegerField("Sender ID")  # Добавляем новое поле sender_id
    sender_type = SelectField(
        "Sender Type",
        choices=[("user", "User")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Send Request")


class AcceptRequestForm(FlaskForm):
    submit = SubmitField("Accept")


class RejectRequestForm(FlaskForm):
    submit = SubmitField("Reject")


class InviteMemberForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    sender_id = IntegerField("Sender ID")  # Добавляем новое поле sender_id
    submit = SubmitField("Invite")
