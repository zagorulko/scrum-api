#!/usr/bin/env python3
import faker

from server import app, models

class Config:
    LANG = 'uk_UA'
    SEED = 13371337
    SUPERUSER = 'joe'
    USER_COUNT = 100
    USER_PASSWORD = '12345'
    PROJECT_COUNT = 10
    PROJECT_MEMBERS_MAX = 30
    SPRINT_COUNT = 100
    TASK_COUNT = 500
    TASK_ASSIGNEES_MAX = 3
    COMMENT_COUNT = 1000

def gen_unique(existing, gen):
    x = None
    ok = False
    while not ok:
        x = gen()
        ok = x not in existing
    return x

class Mocker:
    def __init__(self):
        self.fake = faker.Factory.create(Config.LANG)
        if Config.SEED:
            self.fake.seed(Config.SEED)
        self.superuser = None
        if Config.SUPERUSER:
            self.superuser = models.User.query\
                                .filter_by(username=Config.SUPERUSER).first()

    def mock_users(self):
        print('[*] Users')

        usernames = set()
        if self.superuser:
            usernames.add(self.superuser)
        for i in range(Config.USER_COUNT):
            user = models.User()
            user.username = gen_unique(usernames, lambda: self.fake.user_name())
            user.hash_password(Config.USER_PASSWORD)
            user.full_name = self.fake.first_name()+' '+self.fake.last_name()
            user.email = self.fake.email()

            models.db.session.add(user)
            usernames.add(user.username)

        models.db.session.commit()

    def mock_projects(self):
        print('[*] Projects')

        aliases = set()
        for i in range(Config.PROJECT_COUNT):
            project = models.Project()
            project.alias = gen_unique(aliases, lambda: self.fake.word())
            project.name = self.fake.catch_phrase()
            project.description = self.fake.paragraph()
            project.vcs_link = self.fake.url()
            project.bts_link = self.fake.url()
            project.cis_link = self.fake.url()

            member_query = models.User.query.order_by(models.db.func.random())
            member_count = self.fake.random.randrange(1, Config.PROJECT_MEMBERS_MAX)
            member_count = min(member_count, member_query.count())
            project.members = member_query[:member_count]
            if self.superuser:
                project.members.append(self.superuser)

            models.db.session.add(project)
            aliases.add(project.alias)

        models.db.session.commit()

    def mock_sprints(self):
        print('[*] Sprints')

        for i in range(Config.SPRINT_COUNT):
            sprint = models.Sprint()
            sprint.start_date = self.fake.date_time_between('-2y','1m'),
            sprint.end_date = self.fake.date_time_between('1m', '2m')
            sprint.goal = self.fake.sentence()

            sprint.project = models.Project.query\
                .order_by(models.db.func.random())\
                .first()

            models.db.session.add(sprint)

        models.db.session.commit()

    def mock_tasks(self):
        print('[*] Tasks')

        task_ids = []
        next_bts_ticket = 1
        for i in range(Config.TASK_COUNT):
            task = models.Task()
            task.title = self.fake.sentence()
            task.creation_date = self.fake.date_time_between('-3y', '-1m')
            task.status = self.fake.random.choice([models.TaskStatus.BACKLOG,
                                                   models.TaskStatus.IN_PROCESS])
            task.kind = self.fake.random.choice(list(models.TaskKind))
            task.priority = self.fake.random.randrange(-2, 2)
            if self.fake.boolean(20):
                task.acceptance_criteria = self.fake.paragraph()
            if self.fake.boolean(40):
                task.user_story = self.fake.paragraph()
            if self.fake.boolean(30):
                task.initial_estimate = self.fake.random.randrange(1, 30)
            if self.fake.boolean(30):
                task.vcs_commit = self.fake.sha1()
            if task.kind == models.TaskKind.BUG and self.fake.boolean(60):
                task.bts_ticket = next_bts_ticket
                next_bts_ticket += 1
            if self.fake.boolean(50):
                task.status = models.TaskStatus.DONE
                task.completion_date = self.fake.date_time_between(
                                                            task.creation_date)
                if self.fake.boolean(50):
                    task.time_spent = self.fake.random.randrange(1, 100)
                if self.fake.boolean(50):
                    task.effort = '{0:.2f}'.format(self.fake.random.random()*10)

            task.project = models.Project.query\
                .order_by(models.db.func.random())\
                .first()

            if task.project.sprints and self.fake.boolean(80):
                task.sprint = self.fake.random.choice(task.project.sprints)

            if task_ids and self.fake.boolean(20):
                parent_task_id = self.fake.random.choice(task_ids)
                task.parent_task = models.Task.query.get(parent_task_id)

            task.author = self.fake.random.choice(task.project.members)

            assignee_count = self.fake.random.randrange(1, min(
                                                len(task.project.members),
                                                Config.TASK_ASSIGNEES_MAX))
            task.assignees = task.project.members[:]
            self.fake.random.shuffle(task.assignees)
            task.assignees = task.assignees[:assignee_count]

            models.db.session.add(task)
            models.db.session.flush()
            models.db.session.refresh(task)
            task_ids.append(task.id)

        models.db.session.commit()

    def mock_comments(self):
        print('[*] Comments')

        for i in range(Config.COMMENT_COUNT):
            comment = models.Comment()

            comment.task = models.Task.query\
                .order_by(models.db.func.random())\
                .first()

            comment.author = self.fake.random.choice(comment.task.project.members)

            comment.creation_date = self.fake.date_time_between(
                                                    comment.task.creation_date)
            comment.message = self.fake.paragraph()

            models.db.session.add(comment)

        models.db.session.commit()

    def mock(self):
        if self.superuser:
            models.db.make_transient(self.superuser)
        models.db.session.query(models.Comment).delete()
        models.db.session.query(models.Task).delete()
        models.db.session.query(models.Sprint).delete()
        models.db.session.query(models.Project).delete()
        models.db.session.query(models.User).delete()
        if self.superuser:
            models.db.session.add(self.superuser)
        models.db.session.commit()

        self.mock_users()
        self.mock_projects()
        self.mock_sprints()
        self.mock_tasks()
        self.mock_comments()

def main():
    mocker = Mocker()
    mocker.mock()

if __name__ == '__main__':
    main()
