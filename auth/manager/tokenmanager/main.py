import redis
from flask import Flask, request, abort, g, render_template


app = Flask(__name__)
app.config.from_envvar('TOKENMANAGER_CONFIG')

r = redis.StrictRedis(**app.config['REDIS_CONF'])

import views

app.before_request(views.before_request)
app.add_url_rule('/', 'index', views.index)
app.add_url_rule('/tokens/add', view_func=views.TokenAddView.as_view('create_token'))
app.add_url_rule('/tokens/<token>/delete', view_func=views.delete, methods=['GET'])


if __name__ == "__main__":
    app.run(port=app.config['PORT'])