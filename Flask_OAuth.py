import os
import json
from flask import Flask, redirect, url_for, session, request, jsonify, Markup, make_response
from  flask_oauthlib.client import OAuth

GITHUB_APP_ID = os.getenv('GITHUB_APP_ID', '3090951d090469541b2c')
GITHUB_APP_KEY = os.getenv('GITHUB_APP_ID', 'a9b64214462338af0539cb50e4494c51720c0ad0')

app = Flask(__name__)
app.debug = True
oauth_state="oauth_state"
app.secret_key = 'development'
oauth = OAuth(app)

github = oauth.remote_app(
    'github',
    consumer_key=GITHUB_APP_ID,
    consumer_secret=GITHUB_APP_KEY,
    base_url='https://github.com',
    request_token_url=None,
    request_token_params={'scope': 'user'},
    access_token_url='/login/oauth/access_token',
    authorize_url='/login/oauth/authorize',

)


def json_to_dict(x):
    '''OAuthResponse class can't not parse the JSON data with content-type
    text/html, so we need reload the JSON data manually'''
    if x.find('callback') > -1:
        pos_lb = x.find('{')
        pos_rb = x.find('}')
        x = x[pos_lb:pos_rb + 1]
    try:
        return json.loads(x, encoding='utf-8')
    except:
        return x


def update_qq_api_request_data(data={}):
    '''Update some required parameters for OAuth2.0 API calls'''
    defaults = {
        'openid': session.get('qq_openid'),
        'access_token': session.get('github_token')[0],
        'oauth_consumer_key': GITHUB_APP_ID,
    }
    defaults.update(data)
    return defaults


@app.route('/')
def index():
    ''' 用来放主页 '''
    return Markup('''<meta property="qc:admins" '''
                  '''content="226526754150631611006375" />''')


@app.route('/user_info')
def get_user_info():
    """返回用户信息页面"""
    # if 'github_token' in session:
    #     data = update_qq_api_request_data()
    #     resp = github.get('/user/get_user_info', data=data)
    #     return jsonify(status=resp.status, data=resp.data)
    # return redirect(url_for('login'))
    # get user info with token
    user = github.get('https://api.github.com/user', {'access_token': session['github_token']})
    return json.dumps(user.data)


@app.route('/login')
def login():
    return github.authorize(state=oauth_state, callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('github_token', None)
    return redirect(url_for('get_user_info'))


@app.route('/login/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['github_token'] = (resp['access_token'], '')


    # if isinstance(resp, dict):
    #     session['qq_openid'] = resp.get('openid')
    # return json.dumps(user.data)
    return redirect(url_for('get_user_info'))


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=50000,ssl_context=("server.crt", "server.key"))
    #app.run(host="0.0.0.0",port=50000)
