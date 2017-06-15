import enum

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256

from server import app

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), nullable=False)
)

task_assigments = db.Table(
    'task_assigments',
    db.Model.metadata,
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), nullable=False),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False)
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

    @classmethod
    def load(cls, username):
        return cls.query.filter_by(username=username).first()

    def hash_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)

    members = db.relationship('User', secondary=project_members,
                              back_populates='projects')
    tasks = db.relationship('Task', back_populates='project')
    sprints = db.relationship('Sprint', back_populates='project')

    name = db.Column(db.String)
    description = db.Column(db.Text)
    vcs_link = db.Column(db.String)
    bt_link = db.Column(db.String)
    ci_link = db.Column(db.String)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    project = db.relationship('Project', back_populates='tasks')
    sprint_id = db.Column(db.Integer, db.ForeignKey('sprints.id'))
    sprint = db.relationship('Sprint', back_populates='tasks')
    parent_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    parent_task = db.relationship('Task')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User')
    comments = db.relationship('Comment', back_populates='task')
    responsible = db.relationship('User', secondary=task_assigments)

    order = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(TaskStatus), nullable=False)

    # track = db.Column(db.String)
    vcs_commit = db.Column(db.String)
    initial_estimate = db.Column(db.Integer)
    completion_date = db.Column(db.DateTime)
    time_spent = db.Column(db.Integer)
    effort = db.Column(db.Float)
    kind = db.Column(db.Enum(TaskKind))
    user_story = db.Column(db.Text)
    acceptance_criteria = db.Column(db.Text)
    bt_ticket = db.Column(db.String)

class Sprint(db.Model):
    __tablename__ = 'sprints'
    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    project = db.relationship('Project', back_populates='sprints')
    tasks = db.relationship('Task', back_populates='sprint')

    order = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    goal = db.Column(db.Text)

    def is_completed(self):
        pass

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    task = db.relationship('Task', back_populates='comments')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User')
    added_at = db.Column(db.DateTime)
    message = db.Text()
