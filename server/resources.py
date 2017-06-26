from datetime import datetime, timedelta

from flask import jsonify
from flask_jwt_extended import (JWTManager, jwt_required,
                                create_access_token, get_jwt_identity)
from flask_restful import Api, Resource, reqparse

from server import app, models, schemas

api = Api(app, prefix='/v1')
jwt = JWTManager(app)

class NotFound(Exception):
    pass

class AccessDenied(Exception):
    pass

@app.errorhandler(NotFound)
def handle_not_found(error):
    response = jsonify({'message': 'Not found'})
    response.status_code = 404
    return response

@app.errorhandler(AccessDenied)
def handle_access_denied(error):
    response = jsonify({'message': 'Access denied'})
    response.status_code = 403
    return response

def get_profile():
    return models.User.query.get(get_jwt_identity())

def authorize_project(project):
    if not models.db.session.query(models.project_members)\
             .filter_by(project_id=project.id,
                        user_id=get_jwt_identity())\
             .first():
        raise AccessDenied()

def project_guard(fn):
    def wrapper(self, project_alias):
        project = models.Project.query.filter_by(alias=project_alias).first()
        if not project:
            raise NotFound()
        authorize_project(project)
        return fn(self, project)
    return wrapper

def sprint_guard(fn):
    def wrapper(self, sprint_id):
        sprint = models.Sprint.query.get(sprint_id)
        if not sprint:
            raise NotFound()
        authorize_project(sprint.project)
        return fn(self, sprint)
    return wrapper

def task_guard(fn):
    def wrapper(self, task_id):
        task = models.Task.query.get(task_id)
        if not task:
            raise NotFound()
        authorize_project(task.project)
        return fn(self, task)
    return wrapper

def comment_guard(fn):
    def wrapper(self, comment_id):
        comment = models.Task.query.get(comment_id)
        if not comment:
            raise NotFound()
        authorize_project(comment.task.project)
        return fn(self, comment)
    return wrapper

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        user = models.User.query.filter_by(username=args['username']).first()
        if not user:
            return {'message': 'No such user'}, 401
        if not user.verify_password(args['password']):
            return {'message': 'Invalid password'}, 401
        access_token = create_access_token(identity=user.id)
        return {'access_token': access_token}

class Profile(Resource):
    @jwt_required
    def get(self):
        return schemas.User.dump(get_profile())

    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        parser.add_argument('fullName', type=str)
        parser.add_argument('email', type=str)
        args = parser.parse_args()

        profile = get_profile()
        schemas.User.load(profile, args)

        models.db.session.add(profile)
        models.db.session.commit()

        return {'ok': True}

class Projects(Resource):
    @jwt_required
    def get(self):
        profile = get_profile()
        return {'projects': [schemas.Project.dump(x) for x in profile.projects]}

class Project(Resource):
    @jwt_required
    @project_guard
    def get(self, project):
        return schemas.Project.dump(project)

class ProjectMembers(Resource):
    @jwt_required
    @project_guard
    def get(self, project):
        return {'members': [schemas.User.dump(x) for x in project.members]}

class ProjectSprints(Resource):
    @jwt_required
    @project_guard
    def get(self, project):
        return {'sprints': [schemas.Sprint.dump(x) for x in project.sprints]}

    @jwt_required
    @project_guard
    def post(self):
        pass

class ProjectTasks(Resource):
    @jwt_required
    @project_guard
    def get(self, project):
        profile = get_profile()
        tasks_out = []
        for task in project.tasks:
            t = schemas.Task.dump_short(task)
            t['assignedToMe'] = profile in task.assignees
            tasks_out.append(t)
        return {'tasks': tasks_out}

    @jwt_required
    @project_guard
    def post(self, project):
        parser = reqparse.RequestParser()
        parser.add_argument('sprint', type=int)
        parser.add_argument('parentTask', type=int)
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('kind', type=models.TaskKind, required=True)
        parser.add_argument('priority', type=int, default=0)
        parser.add_argument('acceptanceCriteria', type=str)
        parser.add_argument('userStory', type=str)
        parser.add_argument('initialEstimate', type=int)
        parser.add_argument('assignees', type=str, nargs='*', default=[])
        args = parser.parse_args()

        task = models.Task()
        task.project = project
        schemas.Task.load(task, args)
        for assignee_username in args.assignees:
            task.assignees.append(schemas.User.open(assignee_username))

        models.db.session.add(task)
        models.db.session.commit()

class Sprint(Resource):
    @jwt_required
    @sprint_guard
    def get(self, sprint):
        return schemas.Sprint.dump(sprint)

    @jwt_required
    @sprint_guard
    def put(self, sprint):
        pass

    @jwt_required
    @sprint_guard
    def delete(self, sprint):
        pass

class SprintTasks(Resource):
    @jwt_required
    @sprint_guard
    def get(self, sprint):
        return {'tasks': [schemas.Task.dump_short(x) for x in sprint.tasks]}

class SprintBurndown(Resource):
    @jwt_required
    @sprint_guard
    def get(self, sprint):
        task_count = models.Task.query\
            .filter_by(sprint_id=sprint.id)\
            .count()
        day_count = (sprint.end_date - sprint.start_date).days
        burndown = []
        for day_no in range(day_count):
            d = sprint.start_date + timedelta(days=day_no)
            completed_count = models.Task.query\
                .filter(models.Task.sprint_id == sprint.id,
                        models.Task.completion_date <= d)\
                .count()
            actually_left = task_count - completed_count
            should_be_left = int(task_count - (task_count * (day_no / day_count)))
            burndown.append({
                'date': d.isoformat(),
                'actually_left': actually_left,
                'should_be_left': should_be_left
            })
        return {'burndown': burndown}

class Task(Resource):
    @jwt_required
    @task_guard
    def get(self, task):
        d = schemas.Task.dump_full(task)
        d['assignees'] = [schemas.User.dump(x) for x in task.assignees]
        return d

    @jwt_required
    @task_guard
    def put(self, task):
        pass

    @jwt_required
    @task_guard
    def delete(self, task):
        pass

class TaskComments(Resource):
    @jwt_required
    @task_guard
    def get(self, task):
        return {'comments': [schemas.Comment.dump(x) for x in task.comments]}

    @jwt_required
    @task_guard
    def post(self, task):
        parser = reqparse.RequestParser()
        parser.add_argument('message', type=str, required=True)
        args = parser.parse_args()

        comment = models.Comment()
        comment.task = task
        comment.author = get_profile()
        comment.creation_date = datetime.now()
        comment.message = args['message']

        models.db.session.add(comment)
        models.db.session.commit()

        return {'id': comment.id}

class Comment(Resource):
    @jwt_required
    @comment_guard
    def get(self, comment):
        return schemas.Comment.dump(comment)

api.add_resource(Login, '/login')
api.add_resource(Profile, '/profile')
api.add_resource(Projects, '/projects')
api.add_resource(Project, '/projects/<string:project_alias>')
api.add_resource(ProjectMembers, '/projects/<string:project_alias>/members')
api.add_resource(ProjectSprints, '/projects/<string:project_alias>/sprints')
api.add_resource(ProjectTasks, '/projects/<string:project_alias>/tasks')
api.add_resource(Sprint, '/sprints/<int:sprint_id>')
api.add_resource(SprintTasks, '/sprints/<int:sprint_id>/tasks')
api.add_resource(SprintBurndown, '/sprints/<int:sprint_id>/burndown')
api.add_resource(Task, '/tasks/<int:task_id>')
api.add_resource(TaskComments, '/tasks/<int:task_id>/comments')
api.add_resource(Comment, '/comments/<int:comment_id>')
