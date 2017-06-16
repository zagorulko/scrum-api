from datetime import datetime

from flask import jsonify, request
from flask_jwt_extended import (JWTManager, jwt_required,
                                create_access_token, get_jwt_identity)
from flask_restful import Api, Resource, reqparse

from server import app, models

api = Api(app, prefix='/v1')
jwt = JWTManager(app)

class NotFound(Exception):
    pass

@app.errorhandler(NotFound)
def handle_not_found(error):
    response = jsonify({'message': 'Not found'})
    response.status_code = 404
    return response

@app.errorhandler(models.AccessDenied)
def handle_access_denied(error):
    response = jsonify({'message': 'Access denied'})
    response.status_code = 403
    return response

def load_project(project_alias):
    project = models.Project.query.filter_by(alias=project_alias).first()
    if not project:
        raise NotFound()
    project.authorize(get_jwt_identity())
    return project

def load_task(task_id):
    task = models.Task.query.get(task_id)
    if not task:
        raise NotFound()
    task.authorize(get_jwt_identity())
    return task

def load_sprint(sprint_id):
    sprint = models.Sprint.query.get(sprint_id)
    if not sprint:
        raise NotFound()
    sprint.authorize(get_jwt_identity())
    return sprint

def load_comment(comment_id):
    comment = models.Comment.query.get(comment_id)
    if not comment:
        raise NotFound()
    comment.authorize(get_jwt_identity())
    return comment

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        user = models.User.query.filter_by(username=args.username).first()
        if not user:
            return {'msg': 'No such user'}, 401
        if not user.verify_password(args.password):
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
        return {
            'alias': project.alias,
            'name': project.name,
            'description': project.description,
            'vcs_link': project.vcs_link,
            'bt_link': project.bt_link,
            'ci_link': project.ci_link
        }

class ProjectMembers(Resource):
    @jwt_required
    def get(self, project_alias):
        project = load_project(project_alias)
        members = []
        for member in project.members:
            members.append({
                'username': member.username,
                'full_name': member.full_name,
                'email': member.email
            })
        return {'members': members}

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

        parser = reqparse.RequestParser()
        parser.add_argument('sprint_id', type=int)
        parser.add_argument('parent_task_id', type=int)
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('kind', type=models.TaskKind, required=True)
        parser.add_argument('priority', type=int, default=0)
        parser.add_argument('acceptance_criteria', type=str)
        parser.add_argument('user_story', type=str)
        parser.add_argument('initial_estimate', type=int)
        parser.add_argument('assignees', type=str, nargs='*', default=[])
        args = parser.parse_args()

        task = models.Task()
        task.project_id = project.id
        task.sprint_id = args.sprint_id
        task.parent_task_id = args.parent_task_id
        task.author_id = get_jwt_identity()
        task.title = args.title
        task.creation_date = datetime.utcnow()
        task.kind = args.kind
        task.priority = args.priority
        task.acceptance_criteria = args.acceptance_criteria
        task.user_story = args.user_story
        task.initial_estimate = args.initial_estimate
        for assignee_username in args.assignees:
            assignee = User.query.filter_by(username=assignee_username).first()
            task.assignees.append(assignee.id)

        models.db.session.add(task)
        models.db.session.commit()

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
api.add_resource(ProjectMembers, '/projects/<string:project_alias>/members')
api.add_resource(ProjectSprints, '/projects/<string:project_alias>/sprints')
api.add_resource(ProjectTasks, '/projects/<string:project_alias>/tasks')
api.add_resource(Sprint, '/sprints/<int:sprint_id>')
api.add_resource(SprintTasks, '/sprints/<int:sprint_id>/tasks')
api.add_resource(Task, '/tasks/<int:task_id>')
api.add_resource(TaskComments, '/tasks/<int:task_id>/comments')
api.add_resource(Comment, '/comments/<int:comment_id>')
