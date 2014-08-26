import requests
import urllib

from flask import Blueprint, redirect, request, session
from requests.auth import HTTPBasicAuth

import constants


auth = Blueprint('auth', __name__)


@auth.route('/login')
def create_login_url():
  """Creates and redirects to the Clever Instant Login URL."""

  params = {
    'response_type' : 'code',
    'redirect_uri' : constants.OAUTH_CALLBACK_URL,
    'client_id' : constants.CLIENT_ID,
    'scope' : 'read:user',
    'district_id' : constants.DISTRICT_ID
  }

  return redirect(constants.AUTHORIZE_REQUEST_URL +
                  '?' + urllib.urlencode(params))


@auth.route('/oauth')
def oauth_callback():
  """Handles the Clever Instant Login callback."""

  code = request.args.get('code')
  if not code:
    return redirect('/login')
  else:
    return get_auth_token(code)


def get_auth_token(code):
  """Exchanges an OAUTH code for an OAUTH access token."""

  payload = {
    'code': code,
    'grant_type': 'authorization_code',
    'redirect_uri': constants.OAUTH_CALLBACK_URL
  }

  r = requests.post(constants.TOKEN_REQUEST_URL, data=payload,
      auth=HTTPBasicAuth(constants.CLIENT_ID, constants.CLIENT_SECRET))

  if r.status_code == 200:
    return login_user(r.json()['access_token'])
  else:
    # token request code is invalid, try again
    return redirect('/login')


def login_user(access_token):
  "Logs in the user by creating a temporary session."

  headers = {'Authorization': 'Bearer ' + access_token}
  r = requests.get(constants.IDENTITY_API_URL, headers=headers)

  session['user_id'] = r.json()['data']['id']
  session['type'] = r.json()['data']['type']
  session['name'] = r.json()['data']['name']
  return redirect('/schedule')


@auth.route('/logout')
def logout():
  "Logs out the user by destroying the session."

  session.pop('user_id', None)
  session.pop('type', None)
  session.pop('name', None)
  return redirect('/')


def login_required(func):
  """Annotation to force login for a given path."""

  def inner(*args, **kwargs):
    if 'user_id' not in session:
      return redirect('/login')
    return func(*args, **kwargs)
  return inner
