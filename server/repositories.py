from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from server import app, models

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

def without_nulls(d):
    return {k: v for k, v in d.items() if v != None}

def authorize_user(user):
    pass

def authorize_project(project):
    if not models.db.session.query(models.project_members)\
             .filter_by(project_id=project.id,
                        user_id=get_jwt_identity())\
             .first():
        raise AccessDenied()

class User:
    def open(self, username):
        user = models.User.query.filter_by(username=username).first()
        if not user:
            raise NotFound()
        self.authorize(user)
        return user

    def authorize(self, user):
        authorize_user(user)

    def dump(self, user):
        return {
            'username': user.username,
            'fullName': user.full_name,
            'email': user.email
        }

    def load(self, user, d):
        if 'username' in d:
            user.username = d['username']
        if 'fullName' in d:
            user.full_name = d['fullName']
        if 'email' in d:
            user.email = d['email']

class Project:
    def open(self, project_alias):
        project = models.Project.query.filter_by(alias=project_alias).first()
        if not project:
            raise NotFound()
        self.authorize(project)
        return project

    def authorize(self, project):
        authorize_project(project)

    def dump(self, project):
        return without_nulls({
            'alias': project.alias,
            'name': project.name,
            'description': project.description,
            'vcsLink': project.vcs_link,
            'btsLink': project.bts_link,
            'cisLink': project.cis_link
        })

class Sprint:
    def open(self, sprint_id):
        sprint = models.Sprint.query.get(sprint_id)
        if not sprint:
            raise NotFound()
        self.authorize(sprint)
        return sprint

    def authorize(self, sprint):
        authorize_project(sprint.project)

    def dump(self, sprint):
        return without_nulls({
            'id': sprint.id,
            'startDate': sprint.start_date.isoformat(),
            'endDate': sprint.end_date.isoformat(),
            'goal': sprint.goal
        })

    def load(self, sprint, d):
        if 'startDate' in d:
            sprint.start_date = d['startDate']
        if 'endDate' in d:
            sprint.end_date = d['endDate']
        if 'goal' in d:
            sprint.goal = d['goal']

class Task:
    def open(self, task_id):
        task = models.Task.query.get(task_id)
        if not task:
            raise NotFound()
        self.authorize(task)
        return task

    def authorize(self, task):
        authorize_project(task.project)

    def dump_short(self, task):
        return without_nulls({
            'id': task.id,
            'project': task.project.alias,
            'sprint': task.sprint_id,
            'parentTask': task.parent_task_id,
            'author': task.author.username,
            'title': task.title,
            'creationDate': task.creation_date.isoformat(),
            'status': task.status.name,
            'kind': task.kind.name,
            'priority': task.priority
        })

    def dump_full(self, task):
        d = self.dump_short(task)
        d.update(without_nulls({
            'acceptanceCriteria': task.acceptance_criteria,
            'userStory': task.user_story,
            'initialEstimate': task.initial_estimate,
            'vcsCommit': task.vcs_commit,
            'btsTicket': task.bts_ticket,
            'completionDate': (task.completion_date.isoformat()
                                        if task.completion_date else None),
            'timeSpent': task.time_spent,
            'effort': task.effort
        }))
        return d

    def load(self, task, d):
        if 'sprint' in d:
            if d['sprint'] == None:
                task.sprint = None
            else:
                task.sprint = models.Sprint.get(d['sprint'])
        if 'parentTask' in d:
            if d['parentTask'] == None:
                task.parent_task = None
            else:
                task.parent_task = models.Task.get(d['parentTask'])
        if 'title' in d:
            task.title = d['title']
        if 'status' in d:
            task.status = models.TaskStatus(d['status'])
        if 'kind' in d:
            task.status = models.TaskKind(d['kind'])
        if 'priority' in d:
            taks.priority = d['priority']
        if 'acceptanceCriteria' in d:
            task.acceptance_criteria = d['acceptanceCriteria']
        if 'userStory' in d:
            task.user_story = d['userStory']
        if 'initialEstimate' in d:
            task.initial_estimate = d['initialEstimate']
        if 'vcsCommit' in d:
            task.vcs_commit = d['vcsCommit']
        if 'btsTicket' in d:
            task.bts_ticket = d['btsTicket']
        if 'completionDate' in d:
            task.completion_date = d['completionDate']
        if 'timeSpent' in d:
            task.time_spent = d['timeSpent']

class Comment:
    def open(self, comment_id):
        comment = models.Task.query.get(comment_id)
        if not comment:
            raise NotFound()
        self.authorize(comment)
        return comment

    def authorize(self, comment):
        authorize_project(comment.task.project)

    def dump(self, comment):
        return without_nulls({
            'id': comment.id,
            'task': comment.task.id,
            'author': comment.author.username,
            'creationDate': comment.creation_date.isoformat(),
            'message': comment.message
        })

    def load(self, comment, d):
        if 'message' in d:
            comment.message = d['message']
