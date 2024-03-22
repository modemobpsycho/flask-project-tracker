import unittest
from flask_testing import TestCase
from website import app, db
from website.accounts.forms import (
    LoginForm,
    RegisterForm,
    ProfileForm,
)
from website.projects.forms import (
    AddTaskForm,
    CreateProjectForm,
    ManageMembersForm,
    EditProjectForm,
    AddProjectMemberForm,
    RemoveProjectMemberForm,
    SendJoinRequestForm,
    AcceptRequestForm,
    RejectRequestForm,
    InviteMemberForm,
)


class TestForms(TestCase):
    def create_app(self):
        app.config.from_object("config.TestingConfig")
        return app

    def test_login_form(self):
        form = LoginForm()
        self.assertFalse(form.validate())
        form.email.data = "test@example.com"
        form.password.data = "password"
        self.assertTrue(form.validate())

    def test_profile_form(self):
        form = ProfileForm()
        self.assertFalse(form.validate())
        form.full_name.data = "John Doe"
        form.age.data = 30
        self.assertTrue(form.validate())

    def test_add_task_form(self):
        form = AddTaskForm()
        self.assertFalse(form.validate())
        form.name.data = "Task 1"
        form.description.data = "Description for Task 1"
        self.assertTrue(form.validate())

    def test_create_project_form(self):
        form = CreateProjectForm()
        self.assertFalse(form.validate())
        form.name.data = "Project 1"
        form.description.data = "Description for Project 1"
        self.assertTrue(form.validate())

    def test_manage_members_form(self):
        form = ManageMembersForm()
        self.assertFalse(form.validate())
        form.email.data = "test@example.com"
        self.assertTrue(form.validate())

    def test_add_project_member_form(self):
        form = AddProjectMemberForm()
        self.assertFalse(form.validate())
        form.email.data = "test@example.com"
        form.role.data = "Developer"
        self.assertTrue(form.validate())

    def test_remove_project_member_form(self):
        form = RemoveProjectMemberForm()
        self.assertFalse(form.validate())
        form.member_id.data = "1"
        self.assertTrue(form.validate())

    def test_send_join_request_form(self):
        form = SendJoinRequestForm()
        self.assertFalse(form.validate())
        form.message.data = "Please accept my request."
        form.role.data = "Developer"
        self.assertTrue(form.validate())

    def test_accept_request_form(self):
        form = AcceptRequestForm()
        self.assertFalse(form.validate())
        form.role.data = "Developer"
        self.assertTrue(form.validate())

    def test_reject_request_form(self):
        form = RejectRequestForm()
        self.assertTrue(form.validate())

    def test_invite_member_form(self):
        form = InviteMemberForm()
        self.assertFalse(form.validate())
        form.email.data = "test@example.com"
        form.role.data = "Developer"
        self.assertTrue(form.validate())


if __name__ == "__main__":
    unittest.main()
