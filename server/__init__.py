from flask import Flask

app = Flask(__name__)
app.config.from_object('server.default_config')
app.config.from_envvar('SCRUM_API_CONFIG', silent=True)

import server.commands
import server.models
import server.repositories
import server.resources
