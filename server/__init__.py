from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={"/*": {"origins": "*"}})
app.config.from_object('server.default_config')
app.config.from_envvar('SCRUM_API_CONFIG', silent=True)

import server.commands
import server.models
import server.repositories
import server.resources
