from datetime import datetime

from server import models

def without_nulls(d):
    return {k: v for k, v in d.items() if v != None}

class User:
    @classmethod
    def dump(cls, user):
        return {
            'username': user.username,
            'fullName': user.full_name,
            'email': user.email
        }

    @classmethod
    def load(cls, user, d):
        if 'username' in d:
            user.username = d['username']
        if 'fullName' in d:
            user.full_name = d['fullName']
        if 'email' in d:
            user.email = d['email']

class Project:
    @classmethod
    def dump(cls, project):
        today = datetime.now().date()
        current_sprint = models.Sprint.query\
            .filter(models.Sprint.project_id == project.id,
                    models.Sprint.start_date <= today,
                    models.Sprint.end_date >= today)\
            .first()
        return without_nulls({
            'alias': project.alias,
            'name': project.name,
            'description': project.description,
            'vcsLink': project.vcs_link,
            'btsLink': project.bts_link,
            'cisLink': project.cis_link,
            'currentSprint': (current_sprint.id if current_sprint else None)
        })

class Sprint:
    @classmethod
    def dump(cls, sprint):
        return without_nulls({
            'id': sprint.id,
            'number': sprint.project.sprints.index(sprint) + 1,
            'startDate': sprint.start_date.isoformat(),
            'endDate': sprint.end_date.isoformat(),
            'goal': sprint.goal
        })

    @classmethod
    def load(cls, sprint, d):
        if 'startDate' in d:
            sprint.start_date = d['startDate']
        if 'endDate' in d:
            sprint.end_date = d['endDate']
        if 'goal' in d:
            sprint.goal = d['goal']

class Task:
    @classmethod
    def dump_short(cls, task):
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

    @classmethod
    def dump_full(cls, task):
        d = cls.dump_short(task)
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

    @classmethod
    def load(cls, task, d):
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
        # if 'status' in d:
            # task.status = models.TaskStatus(d['status'])
        # if 'kind' in d:
            # task.status = models.TaskKind(d['kind'])
        if 'priority' in d:
            task.priority = d['priority']
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
    @classmethod
    def dump(cls, comment):
        return without_nulls({
            'id': comment.id,
            'task': comment.task.id,
            'author': comment.author.username,
            'creationDate': comment.creation_date.isoformat(),
            'message': comment.message
        })

    @classmethod
    def load(cls, comment, d):
        if 'message' in d:
            comment.message = d['message']
