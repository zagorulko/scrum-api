from flask import request
from flask_jwt_extended import (JWTManager, jwt_required,
                                create_access_token, get_jwt_identity)
from flask_restful import Resource, Api

from server import app, models

api = Api(app, prefix='/v1', errors={
    'AccessDenied': {
        'message': 'Access denied',
        'status': 403
    },
    'NotFound': {
        'message': 'Not found',
        'status': 404
    }
})
jwt = JWTManager(app)

class NotFound(Exception):
    pass

def load_project(project_alias):
    project = models.Project.query.filter_by(alias=project_alias).first()
    if not project:
        raise NotFound()
    project.authorize(get_jwt_identity())

def load_task(task_id):
    task = models.Task.query.get(task_id)
    if not task:
        raise NotFound()
    task.authorize(get_jwt_identity())

def load_sprint(sprint_id):
    sprint = models.Sprint.query.get(sprint_id)
    if not sprint:
        raise NotFound()
    sprint.authorize(get_jwt_identity())

def load_comment(comment_id):
    comment = models.Comment.query.get(comment_id)
    if not comment:
        raise NotFound()
    comment.authorize(get_jwt_identity())

class Login(Resource):
    def post(self):
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        user = models.User.query.filter_by(username=username).first()
        if not user:
            return {'msg': 'No such user'}, 401
        if not user.verify_password(password):
            return {'msg': 'Invalid password'}, 401
        access_token = create_access_token(identity=user.id)
        return {'access_token': access_token}

class User(Resource):
    @jwt_required
    def get(self):
        user = models.User.query.get(get_jwt_identity())
        return {
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email
        }

    @jwt_required
    def post(self):
        full_name = request.json.get('full_name', None)
        email = request.json.get('email', None)
        user = models.User.query.get(get_jwt_identity())
        user.full_name = full_name
        user.email = email
        models.db.session.add(user)
        models.db.session.commit()
        return {'ok': True}

class UserProjects(Resource):
    @jwt_required
    def get(self):
        user = models.User.query.get(get_jwt_identity())
        projects = []
        for project in user.projects:
            projects.append({
                'alias': project.alias,
                'name': project.name
            })
        return {'projects': projects}

class Project(Resource):
    @jwt_required
    def get(self, project_alias):
        project = load_project(project_alias)

class ProjectSprints(Resource):
    @jwt_required
    def get(self, project_alias):
        project = load_project(project_alias)

    @jwt_required
    def post(self, project_alias):
        project = load_project(project_alias)

class ProjectTasks(Resource):
    @jwt_required
    def get(self, project_alias):
        project = load_project(project_alias)

    @jwt_required
    def post(self, project_alias):
        project = load_project(project_alias)

class Sprint(Resource):
    @jwt_required
    def get(self, sprint_id):
        sprint = load_sprint(sprint_id)

    @jwt_required
    def put(self, sprint_id):
        sprint = load_sprint(sprint_id)

    @jwt_required
    def delete(self, sprint_id):
        sprint = load_sprint(sprint_id)

class SprintTasks(Resource):
    @jwt_required
    def get(self, sprint_id):
        sprint = load_sprint(sprint_id)

class Task(Resource):
    @jwt_required
    def get(self, task_id):
        task = load_task(task_id)

    @jwt_required
    def put(self, task_id):
        task = load_task(task_id)

    @jwt_required
    def delete(self, task_id):
        task = load_task(task_id)

class TaskComments(Resource):
    @jwt_required
    def get(self, task_id):
        task = load_task(task_id)

    @jwt_required
    def post(self, task_id):
        task = load_task(task_id)

class Comment(Resource):
    @jwt_required
    def get(self, comment_id):
        comment = load_comment(comment_id)

    @jwt_required
    def put(self, comment_id):
        comment = load_comment(comment_id)

    @jwt_required
    def delete(self, comment_id):
        comment = load_comment(comment_id)

api.add_resource(Login, '/login')
api.add_resource(User, '/user')
api.add_resource(UserProjects, '/user/projects')
api.add_resource(Project, '/projects/<string:project_alias>')
api.add_resource(ProjectSprints, '/projects/<string:project_alias>/sprints')
api.add_resource(ProjectTasks, '/projects/<string:project_alias>/tasks')
api.add_resource(Sprint, '/sprints/<int:sprint_id>')
api.add_resource(SprintTasks, '/sprints/<int:sprint_id>/tasks')
api.add_resource(Task, '/tasks/<int:task_id>')
api.add_resource(TaskComments, '/tasks/<int:task_id>/comments')
api.add_resource(Comment, '/comments/<int:comment_id>')
