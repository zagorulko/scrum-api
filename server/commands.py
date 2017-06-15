import click

from server import app
from server.models import db, User

@app.cli.command()
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True)
@click.option('--full_name', prompt=True)
@click.option('--email', prompt=True)
def add_user(username, password, full_name, email):
    user = User()
    user.username = username
    user.hash_password(password)
    user.full_name = full_name
    user.email = email
    db.session.add(user)
    db.session.commit()

@app.cli.command()
@click.option('--username', prompt=True)
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    else:
        print('User not found!')
