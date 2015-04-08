import redis

from flask import Flask
app = Flask(__name__)
r = redis.StrictRedis(host='localhost', port=6379, db=0)


@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()