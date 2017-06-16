import enum

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256

from server import app

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class AccessDenied(Exception):
    pass

class TaskKind(enum.Enum):
    FEATURE = 1
    BUG = 2

class TaskStatus(enum.Enum):
    BACKLOG = 1
    IN_PROCESS = 2
    DONE = 3

project_members = db.Table(
    'project_members',
    db.Model.metadata,
    db.Column('user_id', db.Integer,
              db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    db.Column('project_id', db.Integer,
              db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
)

task_assigments = db.Table(
    'task_assigments',
    db.Model.metadata,
    db.Column('task_id', db.Integer,
              db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
    db.Column('user_id', db.Integer,
              db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    projects = db.relationship('Project', secondary=project_members,
                               back_populates='members')

    username = db.Column(db.String, index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    avatar = db.Column(db.String)

    def hash_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)

    members = db.relationship('User', secondary=project_members,
                              back_populates='projects')
    sprints = db.relationship('Sprint', back_populates='project')
    tasks = db.relationship('Task', back_populates='project')

    alias = db.Column(db.String, index=True, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    vcs_link = db.Column(db.String)
    bts_link = db.Column(db.String)
    cis_link = db.Column(db.String)

    def authorize(self, user_id):
        if not db.session.query(project_members)\
                         .filter_by(project_id=self.id, user_id=user_id)\
                         .first():
            raise AccessDenied()

class Sprint(db.Model):
    __tablename__ = 'sprints'
    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    project = db.relationship('Project', back_populates='sprints')
    tasks = db.relationship('Task', back_populates='sprint')

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    goal = db.Column(db.Text)

    def is_completed(self):
        pass

    def authorize(self, user_id):
        self.project.authorize(user_id)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    project = db.relationship('Project', back_populates='tasks')
    sprint_id = db.Column(db.Integer, db.ForeignKey('sprints.id'))
    sprint = db.relationship('Sprint', back_populates='tasks')
    parent_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    parent_task = db.relationship('Task', remote_side=[id])
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User')
    comments = db.relationship('Comment', back_populates='task')
    assignees = db.relationship('User', secondary=task_assigments)

    title = db.Column(db.String, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.BACKLOG)
    kind = db.Column(db.Enum(TaskKind), nullable=False)
    priority = db.Column(db.Integer, default=0)
    acceptance_criteria = db.Column(db.Text)
    user_story = db.Column(db.Text)
    initial_estimate = db.Column(db.Integer)
    vcs_commit = db.Column(db.String)
    bts_ticket = db.Column(db.Integer)
    completion_date = db.Column(db.DateTime)
    time_spent = db.Column(db.Integer)
    effort = db.Column(db.Float)

    def authorize(self, user_id):
        self.project.authorize(user_id)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    task = db.relationship('Task', back_populates='comments')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User')

    creation_date = db.Column(db.DateTime)
    message = db.Text()

    def authorize(self, user_id):
        self.task.authorize(user_id)
