from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional


class TaskForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    status = SelectField(
        "Status",
        choices=[
            ("Pending", "Pending"),
            ("InProgress", "In Progress"),
            ("Completed", "Completed"),
        ],
        default="Pending",
    )
    role = SelectField(
        "Role",
        choices=[
            ("Developer", "Developer"),
            ("QA", "QA"),
            ("Admin", "Admin"),
            ("Project Manager", "Project Manager"),
            ("UX/UI Designer", "UX/UI Designer"),
            ("Other", "Other"),
        ],
        validators=[DataRequired()],
    )


class CommentForm(FlaskForm):
    text = TextAreaField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit")


class HiddenForm(FlaskForm):
    pass
