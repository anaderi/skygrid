from flask import request, abort, g, render_template, redirect
from flask.views import MethodView

from flask_wtf import Form
from wtforms import SelectField
from wtforms import validators

import logic
from cernauth import check_headers


def before_request():
    if not check_headers(request.headers):
        abort(401)


def index():
    username = g.user
    tokens = r.smembers('tokens:' + username)

    return render_template('index.html', username=username, tokens=tokens)


def delete(token):
    username = g.user
    # token = request.form.get('token', type=str)

    if not logic.delete_token(r, token, username):
        abort(403)

    return redirect('/')



class TokenAddView(MethodView):
    def __init__(self):
        self.template = 'create.html'

    def get(self):
        form = TokenCreateForm()
        return render_template(self.template, username=g.user, form=form)

    def post(self):
        form = TokenCreateForm()
        if form.validate_on_submit():
            urls = app.config['SERVICE_URLS'].get(form.data['service'])

            logic.add_token(r, g.user, urls)

            return redirect('/')


        return render_template(self.template, username=g.user, form=form)




from main import app, r

class TokenCreateForm(Form):
    service = SelectField(u'Service', choices=app.config['SERVICES'])
