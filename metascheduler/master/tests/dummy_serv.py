import time
from flask import Flask


app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello():
    time.sleep(1)
    return "Hello!"

if __name__ == "__main__":
    app.run(port=8877)
