from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired


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
