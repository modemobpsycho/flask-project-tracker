from datetime import datetime

from sqlalchemy.orm import relationship

from website import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.now())
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    visibility = db.Column(db.String, nullable=False, default="private")

    creator = relationship("User", backref="created_projects")
    tasks = db.relationship("Task", backref="project", cascade="all, delete-orphan")
    members = db.relationship(
        "ProjectMember", backref="project", cascade="all, delete-orphan"
    )

    def __init__(self, name, creator_id, description=None, visibility="private"):
        self.name = name
        self.creator_id = creator_id
        self.description = description
        self.visibility = visibility

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


class JoinRequest(db.Model):
    __tablename__ = "join_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    sender_type = db.Column(db.String, nullable=False)  # Добавляем поле sender_type
    status = db.Column(db.String, default="pending")
    role = db.Column(db.String)
    message = db.Column(db.String)

    user = db.relationship("User", backref="join_requests")
    project = db.relationship("Project", backref="join_requests")

    def __repr__(self):
        return f"<JoinRequest user_id={self.user_id}, project_id={self.project_id}>"
