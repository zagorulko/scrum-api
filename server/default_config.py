from datetime import timedelta

JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
SECRET_KEY = 'do_not_use_this_key_in_production'
SQLALCHEMY_DATABASE_URI = 'postgres://scrum:scrum@127.0.0.1/scrum'
SQLALCHEMY_TRACK_MODIFICATIONS = False
