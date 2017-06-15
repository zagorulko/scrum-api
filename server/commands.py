import click
import sqlalchemy

from server import app, models

@app.cli.command()
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True)
@click.option('--full_name', prompt=True)
@click.option('--email', prompt=True)
def create_user(username, password, full_name, email):
    user = models.User()
    user.username = username
    user.hash_password(password)
    user.full_name = full_name
    user.email = email
    models.db.session.add(user)
    models.db.session.commit()

@app.cli.command()
@click.option('--username', prompt=True)
def delete_user(username):
    user = models.User.query.filter_by(username=username).first()
    models.db.session.delete(user)
    models.db.session.commit()

@app.cli.command()
@click.option('--alias', prompt=True)
@click.option('--name', prompt=True)
def create_project(alias, name):
    project = models.Project()
    project.alias = alias
    project.name = name
    models.db.session.add(project)
    models.db.session.commit()

@app.cli.command()
@click.option('--alias', prompt=True)
def delete_project(alias):
    project = models.Project.query.filter_by(alias=alias).first()
    models.db.session.delete(project)
    models.db.session.commit()

@app.cli.command()
@click.option('--project-alias', prompt=True)
@click.option('--username', prompt=True)
def add_to_project(project_alias, username):
    project = models.Project.query.filter_by(alias=project_alias).first()
    user = models.User.query.filter_by(username=username).first()
    project.members.append(user)
    models.db.session.add(project)
    models.db.session.commit()

@app.cli.command()
@click.option('--project-alias', prompt=True)
@click.option('--username', prompt=True)
def remove_from_project(project_alias, username):
    project = models.Project.query.filter_by(alias=project_alias).first()
    user = models.User.query.filter_by(username=username).first()
    project.members.remove(user)
    models.db.session.add(project)
    models.db.session.commit()
