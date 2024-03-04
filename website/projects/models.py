from datetime import datetime

from website import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.now())

    tasks = db.relationship("Task", backref="project", cascade="all, delete-orphan")
    members = db.relationship(
        "ProjectMember", backref="project", cascade="all, delete-orphan"
    )

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<Project {self.name}>"


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.now())
    status = db.Column(db.String, nullable=False, default="Pending")
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    def __init__(self, name, description, status, project_id):
        self.name = name
        self.description = description
        self.status = status
        self.project_id = project_id

    def __repr__(self):
        return f"<Task {self.name}>"


class ProjectMember(db.Model):
    __tablename__ = "project_members"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    role = db.Column(db.String)

    def __init__(self, user_id, project_id, role=None):
        self.user_id = user_id
        self.project_id = project_id
        self.role = role

    def __repr__(self):
        return f"<ProjectMember user_id={self.user_id}, project_id={self.project_id}>"


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))

    def __init__(self, text, user_id, task_id=None):
        self.text = text
        self.user_id = user_id
        self.task_id = task_id

    def __repr__(self):
        return f"<Comment {self.text}>"
