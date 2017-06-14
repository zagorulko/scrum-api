import click

from server import app
from server.models import db, User

@app.cli.command()
@click.argument('username')
@click.password_option()
def add_user(username, password):
    user = User()
    user.username = username
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()

@app.cli.command()
@click.argument('username')
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    else:
        print('User not found!')
