from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email


class AddTaskForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Add")


class CreateProjectForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Create")


class ManageMembersForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit_add = SubmitField("Add Member")
    submit_remove = SubmitField("Remove Member")
