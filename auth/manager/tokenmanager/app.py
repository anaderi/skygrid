import redis
from flask import Flask, request, abort, g

from cernauth import check_headers

app = Flask(__name__)
app.config.from_envvar('TOKENMANAGER_CONFIG')


r = redis.StrictRedis(**app.config['REDIS_CONF'])

@app.before_request
def before_request():
    if not check_headers(request.headers):
        abort(401)


@app.route("/")
def hello():
    username = g.user

    return username

if __name__ == "__main__":
    app.run()