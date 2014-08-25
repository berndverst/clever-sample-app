import clever
import json
import os
import requests

from auth import auth, login_required
from flask import Flask, abort, session
from jinja2 import Environment, FileSystemLoader

import constants


app = Flask(__name__)
app.register_blueprint(auth)
# Sets the secret key for session cookie encryption
app.secret_key = constants.SESSION_SECRET_KEY

env = Environment(loader=FileSystemLoader('templates'))

# Sets the Clever OAUTH token for a specific district
clever.set_token(constants.OAUTH_TOKEN)


@app.route('/')
def main():
  template = env.get_template('index.html')
  return template.render()


@app.route('/schedule')
@login_required
def show_schedule():
  """Displays the bell schedule."""

  if session['type'] == 'student':
    field = 'students'
  elif session['type'] == 'teacher':
    field = 'teacher'
  else:
    return abort(400)

  data = clever.Section.all(
      where=json.dumps({field : session['user_id']}),
      sort='period')

  template = env.get_template('schedule.html')
  return template.render(name=session['name']['first'], sections=data)


# For local testing: python main.py
# if __name__ == '__main__':
#   app.run(debug=True, ssl_context='adhoc')
