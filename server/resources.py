from datetime import datetime, timedelta

from flask_jwt_extended import (JWTManager, jwt_required,
                                create_access_token, get_jwt_identity)
from flask_restful import Api, Resource, reqparse

from server import app, models, repositories

api = Api(app, prefix='/v1')
jwt = JWTManager(app)

user_repo = repositories.User()
project_repo = repositories.Project()
sprint_repo = repositories.Sprint()
task_repo = repositories.Task()
comment_repo = repositories.Comment()

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
        profile = models.User.query.get(get_jwt_identity())
        return user_repo.dump(profile)

    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        parser.add_argument('fullName', type=str)
        parser.add_argument('email', type=str)
        args = parser.parse_args()

        profile = models.User.query.get(get_jwt_identity())
        user_repo.load(profile, args)

        models.db.session.add(profile)
        models.db.session.commit()

        return {'ok': True}

class Projects(Resource):
    @jwt_required
    def get(self):
        profile = models.User.query.get(get_jwt_identity())
        return {'projects': [project_repo.dump(x) for x in profile.projects]}

class Project(Resource):
    @jwt_required
    def get(self, project_alias):
        project = project_repo.open(project_alias)
        return project_repo.dump(project)

class ProjectMembers(Resource):
    @jwt_required
    def get(self, project_alias):
        project = project_repo.open(project_alias)
        return {'members': [user_repo.dump(x) for x in project.members]}

class ProjectSprints(Resource):
    @jwt_required
    def get(self, project_alias):
        project = project_repo.open(project_alias)
        return {'sprints': [sprint_repo.dump(x) for x in project.sprints]}

    @jwt_required
    def post(self, project_alias):
        project = project_repo.open(project_alias)

class ProjectTasks(Resource):
    @jwt_required
    def get(self, project_alias):
        profile = models.User.query.get(get_jwt_identity())
        project = project_repo.open(project_alias)
        tasks_out = []
        for task in project.tasks:
            t = task_repo.dump_short(task)
            t['assignedToMe'] = profile in task.assignees
            tasks_out.append(t)
        return {'tasks': tasks_out}

    @jwt_required
    def post(self, project_alias):
        project = project_repo.open(project_alias)

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
        task_repo.load(task, args)
        for assignee_username in args.assignees:
            task.assignees.append(user_repo.open(assignee_username))

        models.db.session.add(task)
        models.db.session.commit()

class Sprint(Resource):
    @jwt_required
    def get(self, sprint_id):
        sprint = sprint_repo.open(sprint_id)
        return sprint_repo.dump(sprint)

    @jwt_required
    def put(self, sprint_id):
        sprint = sprint_repo.open(sprint_id)

    @jwt_required
    def delete(self, sprint_id):
        sprint = sprint_repo.open(sprint_id)

class SprintTasks(Resource):
    @jwt_required
    def get(self, sprint_id):
        sprint = sprint_repo.open(sprint_id)
        return {'tasks': [task_repo.dump_short(x) for x in sprint.tasks]}

class SprintBurndown(Resource):
    @jwt_required
    def get(self, sprint_id):
        sprint = sprint_repo.open(sprint_id)
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
    def get(self, task_id):
        task = task_repo.open(task_id)
        d = task_repo.dump_full(task)
        d['assignees'] = [user_repo.dump(x) for x in task.assignees]
        return d

    @jwt_required
    def put(self, task_id):
        task = task_repo.open(task_id)

    @jwt_required
    def delete(self, task_id):
        task = task_repo.open(task_id)

class TaskComments(Resource):
    @jwt_required
    def get(self, task_id):
        task = task_repo.open(task_id)
        return {'comments': [comment_repo.dump(x) for x in task.comments]}

    @jwt_required
    def post(self, task_id):
        task = task_repo.open(task_id)

class Comment(Resource):
    @jwt_required
    def get(self, comment_id):
        comment = comment_repo.open(comment_id)
        return comment_repo.dump(comment)

    @jwt_required
    def put(self, comment_id):
        comment = comment_repo.open(comment_id)

    @jwt_required
    def delete(self, comment_id):
        comment = comment_repo.open(comment_id)

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
